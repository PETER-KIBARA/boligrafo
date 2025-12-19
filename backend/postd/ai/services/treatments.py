from postd.models import Treatment

def get_treatments(patient):
    return Treatment.objects.filter(patient=patient).order_by("-date")