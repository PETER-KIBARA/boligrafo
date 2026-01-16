from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model 
  
User = get_user_model()  




class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    emergency_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_relation = models.CharField(max_length=50, blank=True, null=True)

    doctor = models.ForeignKey(
        "DoctorProfile",
        on_delete=models.CASCADE,
        related_name="patients",
        null=True,
        blank=True,
    )


    def __str__(self):
        return self.user.username

    @property
    def patient_id(self):
        return self.user.id


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile")
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True)
    national_id = models.CharField(max_length=50, unique=True)
    employee_id = models.CharField(max_length=50, unique=True)
    specialty = models.CharField(max_length=100)
    title = models.CharField(max_length=100)  
    profile_picture = models.ImageField(
        upload_to="doctor_profiles/",
        blank=True,
        null=True
    )  

    def __str__(self):
        return f"Dr. {self.full_name} - {self.specialty}"






class VitalReading(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,  
        on_delete=models.CASCADE,
        related_name="vitals"
    )
    systolic = models.IntegerField()
    diastolic = models.IntegerField()
    heartrate = models.IntegerField(blank=True, null=True)
    symptoms = models.TextField(blank=True, null=True)
    diet = models.TextField(blank=True, null=True)
    exercise = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)




class Prescription(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="prescriptions"
    )
    patient = models.ForeignKey(
        "UserProfile",
        on_delete=models.CASCADE,
        related_name="prescriptions"
    )
    medication = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration_days = models.IntegerField()
    instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.medication} for {self.patient.user.get_full_name()}"

    @property
    def taken_today(self):
        """
        Returns True if the patient has logged any dose for today.
        """
        today = timezone.localdate()
        return self.logs.filter(taken_at__date=today).exists()


class PrescriptionLog(models.Model):
    DOSE_CHOICES = [
        ("morning", "Morning"),
        ("afternoon", "Afternoon"),
        ("evening", "Evening"),
        ("night", "Night"),
    ]

    prescription = models.ForeignKey(
        "Prescription",
        on_delete=models.CASCADE,
        related_name="logs"
    )
    patient = models.ForeignKey(
        "UserProfile",
        on_delete=models.CASCADE
    )
    taken_at = models.DateTimeField(auto_now_add=True)
    dose_time = models.TimeField(default=datetime.time(12, 0))
    dose_label = models.CharField(
        max_length=20,
        choices=DOSE_CHOICES,
        default="morning"
    )

    class Meta:
        ordering = ["-taken_at"]

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.prescription.medication} ({self.dose_label} at {self.dose_time})"




class Treatment(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("pending", "Pending"),
    ]

    patient = models.ForeignKey(
        "UserProfile",
        on_delete=models.CASCADE,
        related_name="treatments",
        null=True, blank=True
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="treatments"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.patient.user.get_full_name() if self.patient else 'No Patient'})"



        



class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('missed_prescription', 'Missed Prescription'),
        ('critical_bp', 'Critical BP Reading'),
        ('general', 'General Notification'),
    ]
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    patient = models.ForeignKey(
        "UserProfile",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='general')
    title = models.CharField(max_length=255, default="Notification")
    message = models.TextField(default="")
    bp_systolic = models.IntegerField(null=True, blank=True)
    bp_diastolic = models.IntegerField(null=True, blank=True)
    missed_days = models.IntegerField(default=0)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'postd_notification'
    
    def __str__(self):
        if self.patient and self.patient.user:
            patient_name = self.patient.user.get_full_name()
        else:
            patient_name = "Unknown Patient"
        return f"{self.notification_type} - {patient_name}"
    
    def get_bp_category(self):
        if self.bp_systolic and self.bp_diastolic:
            if self.bp_systolic >= 180 or self.bp_diastolic >= 120:
                return "Hypertensive Crisis"
            elif self.bp_systolic >= 140 or self.bp_diastolic >= 90:
                return "Stage 2 Hypertension"
            elif self.bp_systolic >= 130 or self.bp_diastolic >= 80:
                return "Stage 1 Hypertension"
            elif self.bp_systolic < 90 or self.bp_diastolic < 60:
                return "Hypotension"
        return "Normal"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("missed", "Missed"),
    ]

    patient = models.ForeignKey("postd.UserProfile", on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey("postd.DoctorProfile", on_delete=models.CASCADE, related_name="appointments", null=True, blank=True)

    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    reason = models.TextField(default="Hypertension follow-up")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.date} {self.time}"


class AISuggestionConfig(models.Model):
    """
    Singleton model to store configuration thresholds for AI Suggestions.
    """
    bp_systolic_threshold = models.IntegerField(default=140, help_text="Systolic BP threshold for warnings")
    bp_diastolic_threshold = models.IntegerField(default=90, help_text="Diastolic BP threshold for warnings")
    trend_slope_threshold = models.FloatField(default=0.5, help_text="Slope threshold for recognizing an increasing BP trend")
    adherence_threshold = models.FloatField(default=0.8, help_text="Minimum adherence rate (0.0 - 1.0) before flagging issues")
    
    class Meta:
        verbose_name = "AI Suggestion Configuration"
        verbose_name_plural = "AI Suggestion Configuration"

    def save(self, *args, **kwargs):
        if not self.pk and AISuggestionConfig.objects.exists():
            # If you want to force singleton behavior aggressively:
            raise Exception("There can be only one AISuggestionConfig instance")
        return super(AISuggestionConfig, self).save(*args, **kwargs)

    def __str__(self):
        return "AI Suggestion Configuration"

    @classmethod
    def get_solitary(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class AISuggestionLog(models.Model):
    """
    Audit trail for AI suggestion requests.
    """
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="ai_requests"
    )
    patient = models.ForeignKey(
        "UserProfile",
        on_delete=models.CASCADE,
        related_name="ai_logs"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    suggestions_generated = models.JSONField(help_text="Snapshot of the suggestions returned")

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"AI Suggestion for {self.patient} by {self.requested_by} at {self.timestamp}"
