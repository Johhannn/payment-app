from datetime import timedelta, datetime
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import User, EMISchedule, Payment, Rule
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import razorpay
from .forms import RuleForm
from .utils.rule_engine import evaluate_rules


# Create your views here.
def user_list(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        role = request.POST.get('role')

        User.objects.create(full_name=full_name, email=email, phone_number=phone_number, password=password, role=role)

        return redirect('success_page')
    return render(request, 'users.html')


def success_page(request):
    return render(request, 'success.html')


def calculate_emi(total_loan, interest_rate, tenure_months):
    if interest_rate == 0:
        return round(total_loan / tenure_months, 2)
    monthly_interest = interest_rate / (12 * 100)
    emi = (total_loan * monthly_interest * (1 + monthly_interest) ** tenure_months) / (
            (1 + monthly_interest) ** tenure_months - 1)
    return round(emi, 2)


def create_emi_schedule(request):
    print(request.POST)
    if request.method == 'POST':
        user = get_object_or_404(User, id=request.POST.get('user'))
        total_loan = request.POST.get('total_loan')
        tenure_months = request.POST.get('tenure_months')
        interest_rate = request.POST.get('interest_rate')
        first_due_date = datetime.strptime(request.POST.get('first_due_date'), "%Y-%m-%d")
        # payment_day = request.POST.get('payment_day')
        emi_amount = calculate_emi(float(total_loan), float(interest_rate), int(tenure_months))
        # schedule_dates = calculate_emi_dates(datetime(first_due_date), int(payment_day), int(tenure_months))
        schedule_dates = [first_due_date + timedelta(days=i * 30) for i in range(int(tenure_months))]

        EMISchedule.objects.bulk_create([
            EMISchedule(
                user=user,
                total_loan=total_loan,
                tenure_months=tenure_months,
                interest_rate=interest_rate,
                emi_amount=emi_amount,
                next_due_date=due_date
            ) for due_date in schedule_dates
        ])

        email_subject = "EMI Schedule Confirmation"
        email_body = f""""
        Dear {user.full_name},

            Your EMI schedule has been successfully created. Below are your due dates:

            {chr(10).join([due_date.strftime('%Y-%m-%d') for due_date in schedule_dates])}

            EMI Amount: {emi_amount} per month
            Total Loan: {total_loan}
            Tenure: {tenure_months} months
            Interest Rate: {interest_rate}%

            Please make sure to pay your EMIs on time.

        Regards,
        Loan Management Team
        """
        send_mail(
            subject=email_subject,
            message=email_body,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return redirect(success_page)

    return render(request, 'emi_schedule.html')


@csrf_exempt
def create_order(request):
    if request.method == "POST":
        try:
            user_id = request.POST.get("user_id")
            amount = request.POST.get("amount")

            if not user_id or not amount:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            user = get_object_or_404(User, id=user_id)
            original_amount = float(amount)
            # amount = int(float(amount) * 100)
            currency = "INR"

            # Create context for rule evaluation
            context = {
                "user": user,
                "amount": original_amount,
                "original_amount": original_amount,
                "course": getattr(user, "course", None),
                # "admission_date": getattr(user, "admission_date", None),
                "payment_date": timezone.now().date(),
                "due_date": getattr(user, "due_date", None),
                "center": getattr(user, "center", None),
                "date": timezone.now(),
                "remarks": "",
                "royalty_share": 0,
            }

            # Evaluate eligibility rules (if any) and block payment if ineligible
            eligibility_rules = evaluate_rules(context, "eligibility")
            print("eligibility_rules: ", eligibility_rules)

            evaluate_rules(context, "calculation")

            adjusted_amount = context.get("amount", original_amount)
            amount_in_paise = int(adjusted_amount * 100)

            razorpay_key_id = settings.RAZORPAY_KEY_ID
            razorpay_key_secret = settings.RAZORPAY_KEY_SECRET
            client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))
            razorpay_order = client.order.create({
                "amount": amount_in_paise,
                "currency": currency,
                "payment_capture": "1"
            })

            # Save payment details in the database
            if razorpay_order['status'] == 'created':
                payment = Payment.objects.create(
                    user=user,
                    amount=adjusted_amount,
                    currency=currency,
                    razorpay_order_id=razorpay_order["id"],
                    status="pending"
                )

                # Action Rules (executed after payment)
                context["payment"] = payment
                evaluate_rules(context, "action")

                payment_data = {
                    "user": payment.user.full_name,
                    "amount": payment.amount,
                    "currency": payment.currency,
                    "razorpay_order_id": payment.razorpay_order_id
                }
                return render(request, "payment.html", {
                    'payment': client,
                    'payment_data': payment_data,
                    "razorpay_key_id": razorpay_key_id,
                    'razorpay_key_secret': razorpay_key_secret
                })

            # print(user, amount, razorpay_order['id'], razorpay_order['status'])
            #    return redirect(f"https://api.razorpay.com/v1/checkout/embedded?order_id={razorpay_order['id']}")

        except Exception as e:
            return render(request, "payment_failed.html", {"error": str(e)})

    return render(request, "payment.html")


def payment_status(request):
    try:
        response = request.POST
        print(response)
        params_dict = {
            'razorpay_order_id': response['razorpay_order_id'],
            'razorpay_payment_id': response['razorpay_payment_id'],
            'razorpay_signature': response['razorpay_signature']
        }

        # Client Instance
        razorpay_key_id = settings.RAZORPAY_KEY_ID
        razorpay_key_secret = settings.RAZORPAY_KEY_SECRET
        client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))

        try:
            status = client.utility.verify_payment_signature(params_dict)
            payment = Payment.objects.get(razorpay_order_id=response['razorpay_order_id'])
            payment.razorpay_payment_id = response['razorpay_payment_id']
            payment.razorpay_signature = response['razorpay_signature']
            payment.status = 'Successful'
            payment.save()
            print("Payment Verification successfull")
            return render(request, "payment_success.html")

        except:
            payment = Payment.objects.get(razorpay_order_id=response['razorpay_order_id'])
            payment.status = "failed"
            payment.save()
            print("Payment verification error")
            return render(request, "payment_failed.html", {"error": "Payment Verification Failed"})
            # return render(request, 'payment_success.html', {'status': False})
    except Exception as e:
        print(e)
        return render(request, "payment_failed.html", {"error": str(e)})


def list_rules(request):
    rules = Rule.objects.all().order_by('priority')
    return render(request, "rule_list.html", {"rules": rules})


def add_rule(request):
    if request.method == "POST":
        form = RuleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_rules')
    else:
        form = RuleForm()
    return render(request, "add_rule.html", {"form": form})


def edit_rule(request, rule_id):
    rule = get_object_or_404(Rule, pk=rule_id)
    if request.method == "POST":
        form = RuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            return redirect('list_rules')
    else:
        form = RuleForm(instance=rule)
    return render(request, "edit_rule.html", {"form": form, "rule": rule})


def delete_rule(request, rule_id):
    rule = get_object_or_404(Rule, pk=rule_id)
    rule.delete()
    return redirect("list_rules")
