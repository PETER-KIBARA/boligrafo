from .context import build_patient_context
from .rules.medication_rules import medication_rules
from .rules.vitals_rules import vitals_rules
from .rules.treatment_rules import treatment_rules
from .rules.appointment_rules import appointment_rules
from .scoring import score_suggestions

def generate_patient_suggestions(patient):
    context = build_patient_context(patient)
    suggestions = []

    suggestions += medication_rules(context)
    suggestions += vitals_rules(context)
    suggestions += treatment_rules(context)
    suggestions += appointment_rules(context)

    return score_suggestions(suggestions)
