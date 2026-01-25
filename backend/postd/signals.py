from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import VitalReading, Notification, UserProfile, Prescription, Appointment

@receiver(post_save, sender=VitalReading)
def create_bp_alert(sender, instance, created, **kwargs):
    if not created:
        return

    patient_user = instance.patient
    patient_profile = UserProfile.objects.filter(user=patient_user).first()
    doctor_profile = getattr(patient_profile, "doctor", None) if patient_profile else None

    if not patient_profile or not doctor_profile:
        print("⚠️ Missing profile links — cannot send alert.")
        return

    doctor_user = doctor_profile.user

    systolic = instance.systolic
    diastolic = instance.diastolic

    if systolic >= 180 or diastolic >= 120:
        notif_type = "critical_bp"
        msg = f"Hypertensive Crisis: {systolic}/{diastolic} mmHg"
    elif systolic > 140 or diastolic > 90:
        notif_type = "critical_bp"
        msg = f"High BP: {systolic}/{diastolic} mmHg"
    elif systolic < 90 or diastolic < 60:
        notif_type = "critical_bp"
        msg = f"Low BP: {systolic}/{diastolic} mmHg"
    else:
        notif_type = "general"
        msg = f"Normal BP: {systolic}/{diastolic} mmHg"

    Notification.objects.create(
        doctor=doctor_user,
        patient=patient_profile,
        notification_type=notif_type,
        title="Blood Pressure Alert",
        message=msg,
        bp_systolic=systolic,
        bp_diastolic=diastolic,
    )

    print(f"✅ BP Alert sent for {patient_user.email}")

    # After saving vitals, check missed logs/prescriptions
    check_missed_prescriptions(patient_profile, doctor_user)
    check_bp_frequency(patient_profile, doctor_user)


def check_missed_prescriptions(patient_profile, doctor_user):
    """
    Checks if the patient missed taking meds (no vitals for 24h).
    """
    last_vital = VitalReading.objects.filter(patient=patient_profile.user).order_by('-created_at').first()

    if not last_vital:
        return

    time_since_last = timezone.now() - last_vital.created_at
    if time_since_last > timedelta(hours=24):
        Notification.objects.create(
            doctor=doctor_user,
            patient=patient_profile,
            notification_type="missed_prescription",
            title="Missed Prescription",
            message=f"{patient_profile.user.first_name} missed recording BP for over 24 hours.",
        )
        print(f"⚠️ Missed prescription alert sent for {patient_profile.user.email}")


def check_bp_frequency(patient_profile, doctor_user):
    """
    Checks if patient logged BP less than twice today.
    """
    today = timezone.now().date()
    readings_today = VitalReading.objects.filter(
        patient=patient_profile.user,
        created_at__date=today
    ).count()

    if readings_today < 2:
        Notification.objects.create(
            doctor=doctor_user,
            patient=patient_profile,
            notification_type="general",
            title="BP Logging Reminder",
            message=f"{patient_profile.user.first_name} has logged BP only {readings_today} time(s) today. Encourage twice daily logging.",
        )
        print(f"🕒 BP logging reminder sent for {patient_profile.user.email}")


@receiver(post_save, sender=Prescription)
def create_prescription_notification(sender, instance, created, **kwargs):
    """
    Create notification when a new prescription is created.
    """
    if not created:
        return
    
    patient_profile = instance.patient
    doctor_user = instance.doctor
    
    if not patient_profile or not doctor_user:
        return
    
    # Notification for the patient
    Notification.objects.create(
        doctor=doctor_user,
        patient=patient_profile,
        notification_type="general",
        title="New Prescription",
        message=f"You have been prescribed {instance.medication} ({instance.dosage}). Take {instance.frequency} for {instance.duration_days} days.",
    )
    
    print(f"✅ Prescription notification sent to {patient_profile.user.email}")


@receiver(post_save, sender=Appointment)
def create_appointment_notification(sender, instance, created, **kwargs):
    """
    Create notification when an appointment is created or updated.
    """
    patient_profile = instance.patient
    doctor_profile = instance.doctor
    
    if not patient_profile:
        return
    
    # Get the doctor's user for the notification
    doctor_user = doctor_profile.user if doctor_profile else None
    
    if created:
        # New appointment
        message = f"New appointment scheduled for {instance.date} at {instance.time}. Reason: {instance.reason}"
        title = "Appointment Scheduled"
    else:
        # Updated appointment
        if instance.status == "cancelled":
            message = f"Your appointment on {instance.date} at {instance.time} has been cancelled."
            title = "Appointment Cancelled"
        elif instance.status == "completed":
            message = f"Your appointment on {instance.date} at {instance.time} has been marked as completed."
            title = "Appointment Completed"
        else:
            message = f"Your appointment has been updated: {instance.date} at {instance.time}. Reason: {instance.reason}"
            title = "Appointment Updated"
    
    Notification.objects.create(
        doctor=doctor_user,
        patient=patient_profile,
        notification_type="general",
        title=title,
        message=message,
    )
    
    print(f"✅ Appointment notification sent to {patient_profile.user.email}")
