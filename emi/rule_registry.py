# rule_registry.py
from datetime import datetime


def festival_discount(context, rule):
    scope = rule.scope or {}
    discount_percent = scope.get("discount_percent", 0)
    eligible_course = scope.get("eligible_course")
    start_date = datetime.fromisoformat(scope.get("start_date", "2000-01-01"))
    end_date = datetime.fromisoformat(scope.get("end_date", "2099-12-31"))

    if context.get("course") == eligible_course and start_date <= context["date"] <= end_date:
        discount = context["amount"] * (discount_percent / 100)
        context["amount"] -= discount


def late_fee_penalty(context, rule):
    scope = rule.scope or {}
    days_late = scope.get("days_late_threshold", 5)
    penalty_amount = scope.get("penalty_amount", 500)

    due_date = context.get("due_date")
    payment_date = context.get("payment_date")

    if due_date and payment_date and (payment_date - due_date).days > days_late:
        context["amount"] += penalty_amount


# Register the functions
RULE_FUNCTIONS = {
    "festival_discount": festival_discount,
    "late_fee_penalty": late_fee_penalty,
}
