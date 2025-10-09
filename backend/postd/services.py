# services.py
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Notification, UserProfile, VitalReading, Prescription
from django.db.models import Count, Q
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationService:
    
    @staticmethod
    def check_missed_prescriptions():
        """
        Check for patients who haven't submitted BP readings twice daily
        """
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Get all doctors
        doctors = User.objects.filter(doctor_profile__isnull=False)
        
        for doctor in doctors:
            # Get doctor's patients
            patients = UserProfile.objects.filter(doctor=doctor.doctor_profile)
            
            for patient in patients:
                # Check readings for today and yesterday
                today_readings = VitalReading.objects.filter(
                    patient=patient.user,
                    created_at__date=today
                ).count()
                
                yesterday_readings = VitalReading.objects.filter(
                    patient=patient.user,
                    created_at__date=yesterday
                ).count()
                
                missed_days = 0
                
                # Check if missed readings today (should have at least 1 reading per day)
                if today_readings == 0:
                    missed_days += 1
                
                # Check if missed readings yesterday
                if yesterday_readings == 0:
                    missed_days += 1
                else:
                    # Reset counter if readings were submitted yesterday
                    missed_days = 1 if today_readings == 0 else 0
                
                # Create notification if missed 2 or more consecutive days
                if missed_days >= 2:
                    # Check if similar notification already exists today
                    existing_notification = Notification.objects.filter(
                        doctor=doctor,
                        patient=patient,
                        notification_type='missed_prescription',
                        created_at__date=today
                    ).exists()
                    
                    if not existing_notification:
                        Notification.objects.create(
                            doctor=doctor,
                            patient=patient,
                            notification_type='missed_prescription',
                            title=f"Missed BP Readings - {missed_days} days",
                            message=f"{patient.user.get_full_name()} has missed BP readings for {missed_days} consecutive days. Last reading was {missed_days} days ago.",
                            missed_days=missed_days
                        )
    
    @staticmethod
    def check_critical_bp_readings():
        """
        Check for critical BP readings in the last 24 hours
        """
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        
        # Get critical BP readings from last 24 hours
        critical_readings = VitalReading.objects.filter(
            created_at__gte=twenty_four_hours_ago
        ).filter(
            Q(systolic__gte=180) | Q(diastolic__gte=120) |  # Hypertensive crisis
            Q(systolic__lt=90) | Q(diastolic__lt=60)        # Hypotension
        )
        
        for reading in critical_readings:
            patient_profile = UserProfile.objects.get(user=reading.patient)
            doctor = patient_profile.doctor.user if patient_profile.doctor else None
            
            if doctor:
                # Check if notification already exists for this reading
                existing_notification = Notification.objects.filter(
                    doctor=doctor,
                    patient=patient_profile,
                    notification_type='critical_bp',
                    bp_systolic=reading.systolic,
                    bp_diastolic=reading.diastolic,
                    created_at__date=reading.created_at.date()
                ).exists()
                
                if not existing_notification:
                    # Determine BP category
                    if reading.systolic >= 180 or reading.diastolic >= 120:
                        bp_category = "Hypertensive Crisis"
                    elif reading.systolic < 90 or reading.diastolic < 60:
                        bp_category = "Hypotension"
                    else:
                        bp_category = "Critical Reading"
                    
                    Notification.objects.create(
                        doctor=doctor,
                        patient=patient_profile,
                        notification_type='critical_bp',
                        title=f"Critical BP Reading - {bp_category}",
                        message=f"{patient_profile.user.get_full_name()} has a critical BP reading of {reading.systolic}/{reading.diastolic} mmHg ({bp_category}).",
                        bp_systolic=reading.systolic,
                        bp_diastolic=reading.diastolic
                    )
    
    @staticmethod
    def generate_all_notifications():
        """
        Run all notification checks
        """
        NotificationService.check_missed_prescriptions()
        NotificationService.check_critical_bp_readings()