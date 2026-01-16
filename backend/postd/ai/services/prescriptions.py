from typing import List, Dict, Any
from datetime import datetime

def _days_between(d1: str, d2: str) -> int:
    # expects ISO timestamps; fallback to 0 on parse error
    try:
        dt1 = datetime.fromisoformat(d1)
        dt2 = datetime.fromisoformat(d2)
        return abs((dt2 - dt1).days)
    except Exception:
        return 0

def analyze_prescriptions(prescriptions: List[Dict[str, Any]], as_of_timestamp: str = None) -> Dict[str, Any]:
    """
    prescriptions: list of dicts, e.g.
    {
      "medication": "Medication A",
      "started_at": "2025-10-01T00:00:00",
      "ended_at": None,  # or ISO timestamp
      "active": True
    }
    Returns signals such as durations, long_on_same_med, repeats
    """
    result = {"med_count": len(prescriptions), "medications": [], "notes": []}
    now_ts = as_of_timestamp
    for p in prescriptions:
        med = p.get("medication")
        started = p.get("started_at")
        ended = p.get("ended_at")
        duration_days = 0
        if started and now_ts:
            duration_days = _days_between(started, now_ts)
        elif started and ended:
            duration_days = _days_between(started, ended)
        entry = {
            "medication": med,
            "active": bool(p.get("active")),
            "duration_days": duration_days,
            "raw": p,
        }
        result["medications"].append(entry)
        if entry["active"] and duration_days >= 56:  # 8 weeks as example threshold
            result["notes"].append(f"{med} active >= {duration_days} days")
    # detect multiple repeats of same med historically
    meds_seen = {}
    for p in prescriptions:
        meds_seen[p.get("medication")] = meds_seen.get(p.get("medication"), 0) + 1
    repeats = [m for m, c in meds_seen.items() if c > 1]
    if repeats:
        result["notes"].append(f"Medication(s) repeated historically: {', '.join(repeats)}")
    return result