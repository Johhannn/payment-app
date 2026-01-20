from ..models import Rule  # Adjust based on your app structure
import traceback


def evaluate_rules(context, rule_type):
    """
    Evaluates rules of a given type with a shared context.
    Supports dynamic calculations, triggers, eligibility checks, and actions.
    """
    applicable_rules = Rule.objects.filter(rule_type=rule_type, is_active=True).order_by("priority")
    print("applicable_rules: ", applicable_rules)
    matched_rules = []

    for rule in applicable_rules:
        try:
            condition_result = eval(rule.condition, {}, context)
            print("condition_result: ", condition_result)

            if condition_result:
                matched_rules.append(rule)
                print("matched_rules: ", matched_rules)

                if rule_type == "calculation" and rule.action:
                    exec(rule.action, {}, context)

                elif rule_type == "action" and rule.action:
                    exec(rule.action, {}, context)

                elif rule_type == "trigger" and rule.action:
                    exec(rule.action, {}, context)

                # eligibility doesn't need action, just pass/fail
        except Exception as e:
            print(f"⚠️ Error in rule '{rule.name}' (Type: {rule_type})")
            print("Condition:", rule.condition)
            print("Action   :", rule.action)
            traceback.print_exc()
            continue

    return matched_rules
