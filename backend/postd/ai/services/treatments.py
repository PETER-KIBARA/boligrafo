from typing import List, Dict, Any

def analyze_treatments(treatments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    treatments: list of treatment episodes:
    {
      "treatment": "Therapy X",
      "started_at": "...",
      "ended_at": "...",
      "outcome": "improved" | "no_change" | "worse" | None
    }
    Returns:
      last_outcome, no_improvement_count, notes
    """
    result = {"count": len(treatments), "last_outcome": None, "no_improvement_count": 0, "notes": []}
    if not treatments:
        result["notes"].append("No treatments recorded")
        return result
    last = treatments[-1]
    result["last_outcome"] = last.get("outcome")
    for t in treatments:
        if t.get("outcome") in ("no_change", "worse", None):
            result["no_improvement_count"] += 1
    if result["no_improvement_count"] > max(1, len(treatments) // 2):
        result["notes"].append("Majority of treatments show no clear improvement")
    return result