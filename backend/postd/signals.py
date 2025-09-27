from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from .models import VitalReading, Notification, Prescription

@receiver(post_save, sender=VitalReading)
def check_vitals(sender, instance, created, **kwargs):
    if not created:
        return
    
    patient = instance.patient
    doctor = getattr(patient, "assigned_doctor", None)  # adjust if you use another link
    if not doctor:
        return

    # ✅ Check abnormal vitals
    alerts = []
    if instance.systolic > 180 or instance.diastolic > 120:
        alerts.append(f"Critical high BP {instance.systolic}/{instance.diastolic}")
    elif instance.systolic < 90 or instance.diastolic < 60:
        alerts.append(f"Low BP {instance.systolic}/{instance.diastolic}")

    if instance.heartrate and (instance.heartrate < 50 or instance.heartrate > 120):
        alerts.append(f"Abnormal HR {instance.heartrate} bpm")

    for msg in alerts:
        Notification.objects.create(
            doctor=doctor,
            patient=patient,
            title="Abnormal Vital Reading",
            message=f"{patient.user.get_full_name()} - {msg}"
        )
