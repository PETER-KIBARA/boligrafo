from datetime import timedelta
from django.utils.timezone import now
from ..schemas import suggestion

MAX_DAYS = 60

def medication_rules(context):
    results = []
    prescriptions = context["prescriptions"]

    for p in prescriptions:
        days = (now().date() - p.start_date).days

        if days >= MAX_DAYS:
            results.append(
                suggestion(
                    "MEDICATION_REVIEW",
                    f"{p.medication} used for {days} days. Consider review or alternative.",
                    "medium",
                    "prescriptions"
                )
            )
    return results
