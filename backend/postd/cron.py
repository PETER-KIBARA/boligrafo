from datetime import timedelta
from django.utils import timezone
from postd.models import Prescription, PrescriptionLog, Notification

def check_missed_prescriptions():
    now = timezone.now()
    for prescription in Prescription.objects.all():
        last_log = prescription.logs.order_by('-taken_at').first()
        if not last_log or (now - last_log.taken_at).days >= 1:
            Notification.objects.create(
                doctor=prescription.doctor,
                patient=prescription.patient,
                notification_type='missed_prescription',
                title='Missed Medication',
                message=f"{prescription.patient.user.get_full_name()} missed their scheduled dose of {prescription.medication}.",
                missed_days=(now - last_log.taken_at).days if last_log else 1
            )
