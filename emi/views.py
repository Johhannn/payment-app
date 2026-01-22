from datetime import timedelta, datetime
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import User, EMISchedule, Payment, Rule
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, EMIScheduleSerializer, PaymentSerializer, RuleSerializer
from .utils.rule_engine import evaluate_rules
from .utils.rule_engine import evaluate_rules
import razorpay
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def user_list(request):
    if request.method == 'POST':
        # Check for admin permission
        if request.user.role != 'Admin':
             return Response({"error": "Only Admins can create users"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def success_page(request):
    return Response({"message": "Operation Successful"}, status=status.HTTP_200_OK)

def calculate_emi(total_loan, interest_rate, tenure_months):
    if interest_rate == 0:
        return round(total_loan / tenure_months, 2)
    monthly_interest = interest_rate / (12 * 100)
    emi = (total_loan * monthly_interest * (1 + monthly_interest) ** tenure_months) / (
            (1 + monthly_interest) ** tenure_months - 1)
    return round(emi, 2)

@api_view(['POST'])
def create_emi_schedule(request):
    user_id = request.data.get('user')
    user = get_object_or_404(User, id=user_id)
    total_loan = float(request.data.get('total_loan'))
    tenure_months = int(request.data.get('tenure_months'))
    interest_rate = float(request.data.get('interest_rate'))
    first_due_date_str = request.data.get('first_due_date') # Format: YYYY-MM-DD
    first_due_date = datetime.strptime(first_due_date_str, "%Y-%m-%d")

    emi_amount = calculate_emi(total_loan, interest_rate, tenure_months)
    schedule_dates = [first_due_date + timedelta(days=i * 30) for i in range(tenure_months)]

    schedules = EMISchedule.objects.bulk_create([
        EMISchedule(
            user=user,
            total_loan=total_loan,
            tenure_months=tenure_months,
            interest_rate=interest_rate,
            emi_amount=emi_amount,
            next_due_date=due_date
        ) for due_date in schedule_dates
    ])

    # Send Email (Optimistic, not blocking)
    try:
        email_subject = "EMI Schedule Confirmation"
        email_body = f"""
        Dear {user.full_name},

            Your EMI schedule has been successfully created.
            
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
            fail_silently=True,
        )
    except Exception as e:
        print(f"Email sending failed: {e}")

    serializer = EMIScheduleSerializer(schedules, many=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def create_order(request):
    try:
        user_id = request.data.get("user_id")
        amount = request.data.get("amount")

        if not user_id or not amount:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)
        original_amount = float(amount)
        currency = "INR"

        context = {
            "user": user,
            "amount": original_amount,
            "original_amount": original_amount,
            "course": getattr(user, "course", None),
            "payment_date": timezone.now().date(),
            "due_date": getattr(user, "due_date", None),
            "center": getattr(user, "center", None),
            "date": timezone.now(),
            "remarks": "",
            "royalty_share": 0,
        }

        evaluate_rules(context, "eligibility")
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

        if razorpay_order['status'] == 'created':
            payment = Payment.objects.create(
                user=user,
                amount=adjusted_amount,
                currency=currency,
                razorpay_order_id=razorpay_order["id"],
                status="pending"
            )

            context["payment"] = payment
            evaluate_rules(context, "action")

            return Response({
                "razorpay_order_id": razorpay_order["id"],
                "razorpay_key_id": razorpay_key_id,
                "amount": amount_in_paise,
                "currency": currency,
                "user_name": user.full_name,
                "user_email": user.email,
                "user_phone": user.phone_number
            })
        
        return Response({"error": "Failed to create order with Razorpay"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def payment_status(request):
    try:
        response = request.data
        razorpay_order_id = response.get('razorpay_order_id')
        razorpay_payment_id = response.get('razorpay_payment_id')
        razorpay_signature = response.get('razorpay_signature')

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })

            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'Successful'
            payment.save()

            return Response({"status": "Payment Verified Successfully"})

        except Exception as e:
            if 'payment' in locals():
                payment.status = "failed"
                payment.save()
            return Response({"error": "Payment Verification Failed", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def rule_list(request):
    if request.method == 'GET':
        rules = Rule.objects.all().order_by('priority')
        serializer = RuleSerializer(rules, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = RuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
def rule_detail(request, pk):
    rule = get_object_or_404(Rule, pk=pk)

    if request.method == 'PUT':
        serializer = RuleSerializer(rule, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        rule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
