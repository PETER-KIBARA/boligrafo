SEVERITY_ORDER = {"high": 3, "medium": 2, "low": 1}

def score_suggestions(suggestions):
    return sorted(
        suggestions,
        key=lambda s: SEVERITY_ORDER.get(s["severity"], 0),
        reverse=True
    )
