from django.utils.timezone import now
from .models import MedicationReminder, VitalReading, Notification

def check_missed_doses():
    reminders = MedicationReminder.objects.filter(due_time__lt=now(), taken=False)
    for reminder in reminders:
        Notification.objects.create(
            user=reminder.patient.user,
            type="missed_dose",
            message=f"Missed dose for {reminder.medication} at {reminder.due_time}."
        )

def check_abnormal_vitals():
    readings = VitalReading.objects.filter(created_at__date=now().date())
    for reading in readings:
        if reading.systolic > 140 or reading.systolic < 90 or reading.diastolic > 90:
            Notification.objects.create(
                user=reading.patient,
                type="abnormal_vital",
                message=f"Abnormal BP: {reading.systolic}/{reading.diastolic}."
            )
