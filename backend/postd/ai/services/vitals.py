from postd.models import VitalReading

def get_vitals(patient):
    return VitalReading.objects.filter(patient=patient).order_by("created_at")[:20]