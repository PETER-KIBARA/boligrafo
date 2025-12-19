from django.utils.timezone import now
from ..schemas import suggestion

def appointment_rules(context):
    results = []
    appointments = context["appointments"]

    missed = [
        a for a in appointments
        if a.date < now().date() and not a.attended
    ]

    if missed:
        results.append(
            suggestion(
                "MISSED_APPOINTMENT",
                f"{len(missed)} missed appointment(s). Follow-up recommended.",
                "low",
                "appointments"
            )
        )

    return results
