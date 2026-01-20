from django.db import models
from django.utils.timezone import now
import uuid


# Create your models here.
class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    password = models.TextField()
    role = models.CharField(max_length=50, choices=[('Admin', 'Admin'), ('Student', 'Student')])
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.full_name


class EMISchedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_loan = models.DecimalField(max_digits=15, decimal_places=2)
    tenure_months = models.IntegerField()
    interest_rate = models.FloatField()
    emi_amount = models.DecimalField(max_digits=15, decimal_places=2)
    # payment_day=models.IntegerField()
    next_due_date = models.DateTimeField()


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('created', 'Created'),
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed')
    ], default="created")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.user} - {self.status}"


class Rule(models.Model):
    RULE_TYPES = (
        ('calculation', 'Calculation'),
        ('eligibility', 'Eligibility'),
        ('trigger', 'Trigger'),
        ('action', 'Action'),
    )

    name = models.CharField(max_length=100)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    condition = models.TextField(help_text="Python-executable condition logic")
    action = models.TextField(blank=True, help_text="Python-executable action logic")
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=1)
    scope = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.rule_type})"
