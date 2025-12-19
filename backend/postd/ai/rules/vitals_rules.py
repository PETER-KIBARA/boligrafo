from ..schemas import suggestion

def vitals_rules(context):
    results = []
    vitals = context["vitals"]

    if len(vitals) >= 3:
        high_readings = [
            v for v in vitals[:5]
            if v.systolic >= 140 or v.diastolic >= 90
        ]

        if len(high_readings) >= 3:
            results.append(
                suggestion(
                    "BP_UNCONTROLLED",
                    "Multiple recent high BP readings detected.",
                    "high",
                    "vitals"
                )
            )

    return results
