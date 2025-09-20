from django.db import models
from django.contrib.auth.models import User
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



class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile")
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True)
    national_id = models.CharField(max_length=50, unique=True)
    employee_id = models.CharField(max_length=50, unique=True)
    specialty = models.CharField(max_length=100)
    title = models.CharField(max_length=100)  # e.g. Consultant, Resident, Specialist


    def __str__(self):
        return f"Dr. {self.full_name} - {self.specialty}"






class VitalReading(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vitals")
    systolic = models.IntegerField()
    diastolic = models.IntegerField()
    heartrate = models.IntegerField(blank=True, null=True)
    symptoms = models.TextField(blank=True, null=True)
    diet = models.TextField(blank=True, null=True)
    exercise = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.patient.username} - {self.systolic}/{self.diastolic} mmHg"
