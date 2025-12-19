from postd.models import Prescription

def get_prescriptions(patient):
    return Prescription.objects.filter(patient=patient).order_by("-start_date")