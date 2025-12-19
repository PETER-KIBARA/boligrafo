from postd.models import Appointment

def get_appointments(patient):
    return Appointment.objects.filter(patient=patient).order_by("-date")