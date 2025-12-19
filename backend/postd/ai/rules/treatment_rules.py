from ..schemas import suggestion

def treatment_rules(context):
    results = []
    treatments = context["treatments"]

    if len(treatments) >= 3:
        results.append(
            suggestion(
                "TREATMENT_REVIEW",
                "Multiple treatments recorded. Consider reassessing treatment plan.",
                "medium",
                "treatments"
            )
        )

    return results
