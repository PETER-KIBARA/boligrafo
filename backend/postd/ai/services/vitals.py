from typing import List, Dict, Any
import math

def _linear_slope(values: List[float]) -> float:
    """
    Compute slope using simple linear regression (least squares).
    Returns slope per index increment. If not enough points, return 0.0
    """
    n = len(values)
    if n < 2:
        return 0.0
    xs = list(range(n))
    x_mean = sum(xs) / n
    y_mean = sum(values) / n
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, values))
    den = sum((x - x_mean) ** 2 for x in xs)
    if den == 0:
        return 0.0
    return num / den

def analyze_vitals(vitals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Expected vitals format: list of readings ordered oldest -> newest
    Each reading is a dict, e.g.:
      {
        "timestamp": "2025-12-01T10:00:00Z",
        "systolic": 140,
        "diastolic": 90,
        "heart_rate": 78
      }
    Returns summary and signals:
      {
        "count": int,
        "last": {...},
        "avg_systolic_30": float or None,
        "avg_diastolic_30": float or None,
        "systolic_slope": float,
        "diastolic_slope": float,
        "notes": [...]
      }
    """
    result = {"count": 0, "last": None, "avg_systolic_30": None, "avg_diastolic_30": None,
              "systolic_slope": 0.0, "diastolic_slope": 0.0, "notes": []}
    if not vitals:
        result["notes"].append("No vitals available")
        return result
    result["count"] = len(vitals)
    result["last"] = vitals[-1]
    # consider last N readings (configurable; here use up to 30)
    recent = vitals[-30:]
    systolics = [r.get("systolic") for r in recent if r.get("systolic") is not None]
    diastolics = [r.get("diastolic") for r in recent if r.get("diastolic") is not None]
    if systolics:
        result["avg_systolic_30"] = sum(systolics) / len(systolics)
        result["systolic_slope"] = _linear_slope(systolics)
    if diastolics:
        result["avg_diastolic_30"] = sum(diastolics) / len(diastolics)
        result["diastolic_slope"] = _linear_slope(diastolics)
    # simple stability/deterioration notes
    if result["systolic_slope"] > 0.25:
        result["notes"].append("Systolic trend rising")
    elif result["systolic_slope"] < -0.25:
        result["notes"].append("Systolic trend falling")
    else:
        result["notes"].append("Systolic trend stable")
    if result["diastolic_slope"] > 0.2:
        result["notes"].append("Diastolic trend rising")
    elif result["diastolic_slope"] < -0.2:
        result["notes"].append("Diastolic trend falling")
    else:
        result["notes"].append("Diastolic trend stable")
    return result