from typing import Dict, Any, List
from .vitals import analyze_vitals
from .prescriptions import analyze_prescriptions
from .treatments import analyze_treatments
from .appointments import analyze_appointments

class SuggestionEngine:
    """
    Rule-based suggestion engine that receives a resolved patient profile dict:
      {
        "patient_id": ...,
        "vitals": [...],
        "prescriptions": [...],
        "treatments": [...],
        "appointments": [...],
        "as_of": "2025-12-10T12:00:00"
      }
    Returns a list of suggestion dicts with fields:
      rule_id, message, evidence, severity, confidence
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def evaluate(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        suggestions = []
        vitals = analyze_vitals(profile.get("vitals", []))
        pres = analyze_prescriptions(profile.get("prescriptions", []), as_of_timestamp=profile.get("as_of"))
        treats = analyze_treatments(profile.get("treatments", []))
        appts = analyze_appointments(profile.get("appointments", []))

        # Rule R001: Medication duration > threshold and vitals stagnant -> flag review
        for med in pres["medications"]:
            if med["active"] and med["duration_days"] >= 56:
                # check vitals stagnation: slopes near zero AND averages not favorable
                sys_slope = vitals.get("systolic_slope", 0.0)
                dia_slope = vitals.get("diastolic_slope", 0.0)
                avg_sys = vitals.get("avg_systolic_30")
                if abs(sys_slope) < 0.25 and (avg_sys is not None and avg_sys >= 140):
                    suggestions.append({
                        "rule_id": "R001",
                        "message": f"Patient has been on {med['medication']} for {med['duration_days']} days with minimal improvement in systolic BP. Consider medication review.",
                        "evidence": {"medication": med, "vitals_summary": vitals},
                        "severity": "high",
                        "confidence": 0.88
                    })

        # Rule R002: Repeated high BP despite compliance -> suggest alternative therapy
        last = vitals.get("last") or {}
        if last.get("systolic") and last.get("systolic") >= 140:
            # naive compliance assumption: if active meds present treat as compliant (real system should check)
            if any(m.get("active") for m in pres["medications"]):
                suggestions.append({
                    "rule_id": "R002",
                    "message": "Recent BP readings remain high while patient is on active medication(s). Consider reviewing adherence and alternative therapies.",
                    "evidence": {"last_vitals": last, "prescriptions": pres},
                    "severity": "high",
                    "confidence": 0.78
                })

        # Rule R003: Missed appointments -> adherence counseling
        if appts.get("missed_ratio", 0.0) >= 0.3:
            suggestions.append({
                "rule_id": "R003",
                "message": "Patient missed >30% of appointments. Suggest adherence counseling and checking barriers to attendance.",
                "evidence": {"appointments": appts},
                "severity": "medium",
                "confidence": 0.82
            })

        # Rule R004: Vitals improving -> continue
        if (vitals.get("systolic_slope", 0.0) < -0.25) or (vitals.get("diastolic_slope", 0.0) < -0.2):
            suggestions.append({
                "rule_id": "R004",
                "message": "Vitals show a clear improving trend. Continue current management and monitor.",
                "evidence": {"vitals": vitals},
                "severity": "low",
                "confidence": 0.85
            })

        # Rule R005: No improvement after multiple treatments -> consider specialist review
        if treats.get("no_improvement_count", 0) >= 2:
            suggestions.append({
                "rule_id": "R005",
                "message": "Multiple treatments with little improvement. Consider specialist referral or multidisciplinary review.",
                "evidence": {"treatments": treats},
                "severity": "medium",
                "confidence": 0.8
            })

        # Rule R006: High BP Alert (Untreated of General)
        last_sys = last.get("systolic") or 0
        last_dia = last.get("diastolic") or 0
        has_active_meds = any(m.get("active") for m in pres["medications"])

        if last_sys >= 160 or last_dia >= 100:
            suggestions.append({
                "rule_id": "R006",
                "message": f"Critical BP Reading ({last_sys}/{last_dia} mmHg). Immediate clinical attention recommended.",
                "evidence": {"last_vitals": last},
                "severity": "high",
                "confidence": 0.95
            })
        elif (last_sys >= 140 or last_dia >= 90) and not has_active_meds:
            suggestions.append({
                "rule_id": "R006",
                "message": f"High BP Reading ({last_sys}/{last_dia} mmHg) without active medication. Consider initiating antihypertensive therapy.",
                "evidence": {"last_vitals": last},
                "severity": "medium",
                "confidence": 0.9
            })

        # Always include a brief rationale summary
        for s in suggestions:
            if "rationale" not in s:
                s["rationale"] = "Rule-based suggestion generated from aggregated signals. See evidence for details."

        return suggestions