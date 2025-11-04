from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
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
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="prescriptions"
    )
    patient = models.ForeignKey(
        "UserProfile", on_delete=models.CASCADE, related_name="prescriptions"
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



        
class PrescriptionLog(models.Model):
    prescription = models.ForeignKey("Prescription", on_delete=models.CASCADE, related_name="logs")
    taken_at = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey("UserProfile", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.prescription.medication}"



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