from typing import List, Dict, Any

def analyze_appointments(appointments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    appointments: list of dicts:
    {
      "scheduled_at": "...",
      "attended": True|False|None
    }
    Returns missed count, ratio, and notes
    """
    result = {"count": len(appointments), "missed": 0, "missed_ratio": 0.0, "notes": []}
    if not appointments:
        result["notes"].append("No appointments recorded")
        return result
    missed = sum(1 for a in appointments if a.get("attended") is False)
    result["missed"] = missed
    result["missed_ratio"] = missed / len(appointments)
    if result["missed_ratio"] >= 0.3:
        result["notes"].append("High missed appointment rate")
    elif result["missed_ratio"] >= 0.1:
        result["notes"].append("Moderate missed appointment rate")
    else:
        result["notes"].append("Good appointment adherence")
    return result