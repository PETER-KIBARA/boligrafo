from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import VitalReading, Notification, UserProfile

@receiver(post_save, sender=VitalReading)
def generate_vital_alert(sender, instance, created, **kwargs):
    """Generate alerts for both patient and doctor when vitals are abnormal."""
    if not created:
        return

    systolic = instance.systolic
    diastolic = instance.diastolic
    patient_user = instance.patient

    try:
        patient_profile = UserProfile.objects.get(user=patient_user)
        doctor = patient_profile.doctor.user if patient_profile.doctor else None
    except UserProfile.DoesNotExist:
        patient_profile = None
        doctor = None

    # Define severity
    if systolic >= 180 or diastolic >= 120:
        severity = "Hypertensive Crisis"
    elif systolic >= 140 or diastolic >= 90:
        severity = "Stage 2 Hypertension"
    elif systolic >= 130 or diastolic >= 80:
        severity = "Stage 1 Hypertension"
    elif systolic < 90 or diastolic < 60:
        severity = "Hypotension"
    else:
        severity = None

    if not severity:
        return  # No alert if vitals are normal

    # Create alert for doctor (if assigned)
    if doctor:
        Notification.objects.create(
            doctor=doctor,
            patient=patient_profile,
            notification_type="critical_bp",
            title=f"Critical BP Alert: {severity}",
            message=(
                f"Patient {patient_user.get_full_name()} recorded "
                f"{systolic}/{diastolic} mmHg ({severity}). Review recommended."
            ),
            bp_systolic=systolic,
            bp_diastolic=diastolic,
            created_at=timezone.now(),
        )

    # Create alert for patient
    Notification.objects.create(
        doctor=doctor or patient_user,
        patient=patient_profile,
        notification_type="critical_bp",
        title=f"Your Blood Pressure is {severity}",
        message=(
            f"Your recent reading was {systolic}/{diastolic} mmHg ({severity}). "
            f"Please follow your doctor’s advice or seek medical attention if you feel unwell."
        ),
        bp_systolic=systolic,
        bp_diastolic=diastolic,
        created_at=timezone.now(),
    )
