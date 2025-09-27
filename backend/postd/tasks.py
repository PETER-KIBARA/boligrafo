from django.utils.timezone import now
from datetime import timedelta
from .models import VitalReading, Prescription, Notification, UserProfile

# Helper to avoid duplicate spam
def create_notification(doctor, patient, message):
    if not Notification.objects.filter(
        doctor=doctor,
        patient=patient,
        message=message,
        created_at__date=now().date()
    ).exists():
        Notification.objects.create(
            doctor=doctor,
            patient=patient,
            message=message
        )

def check_missing_vitals():
    today = now().date()
    for patient in UserProfile.objects.all():
        has_vitals = VitalReading.objects.filter(
            patient=patient.user,
            created_at__date=today
        ).exists()
        if not has_vitals:
            for doc in patient.doctors.all():  # if you’ve got a reverse M2M
                create_notification(doc, patient, "No vitals submitted today.")

def check_abnormal_vitals():
    today = now().date()
    abnormal = VitalReading.objects.filter(created_at__date=today).filter(
        models.Q(systolic__gt=140) | models.Q(diastolic__gt=90)
    )
    for reading in abnormal:
        for doc in reading.patient.userprofile.doctors.all():
            msg = f"Abnormal reading: {reading.systolic}/{reading.diastolic}"
            create_notification(doc, reading.patient.userprofile, msg)

def check_missed_prescriptions():
    yesterday = now().date() - timedelta(days=1)
    missed = Prescription.objects.filter(
        scheduled_date=yesterday,  # you’ll need this field
        taken=False
    )
    for prescription in missed:
        create_notification(
            prescription.doctor,
            prescription.patient,
            f"Missed dose: {prescription.medication}"
        )
