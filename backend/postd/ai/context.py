from .services.vitals import get_vitals
from .services.prescriptions import get_prescriptions
from .services.treatments import get_treatments
from .services.appointments import get_appointments

def build_patient_context(patient):
    return {
        "patient": patient,
        "vitals": get_vitals(patient.user),
        "prescriptions": get_prescriptions(patient.user),
        "treatments": get_treatments(patient.user),
        "appointments": get_appointments(patient.user),
    }
