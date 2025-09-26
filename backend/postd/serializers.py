from rest_framework import serializers
from  .models import UserProfile
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from .models import DoctorProfile
from .models import VitalReading
from .models import Prescription



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
        depth = 1

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password")

        token, _ = Token.objects.get_or_create(user=user)

        return {
            "error": False,
            "token": token.key,
            "name": user.get_full_name() or user.username,  
            "message": "Login successful"
        }


class DoctorProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)


    class Meta:
        model = DoctorProfile
        fields = [
            "id", "full_name", "phone", "national_id",
            "employee_id", "specialty", "title", "email", "username", "profile_picture"
        ]

        

class VitalReadingSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.username", read_only=True)
    patient_email = serializers.CharField(source="patient.email", read_only=True)

    class Meta:
        model = VitalReading
        fields = ["id", "patient", "patient_name", "patient_email", "systolic", "diastolic", "heartrate", "symptoms", "diet", "exercise","created_at"]
        read_only_fields = ["id", "patient_name", "patient_email", "created_at", "patient"]

class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "first_name", "last_name", "email", "phone"]

class PatientSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    last_reading = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["id", "first_name", "last_name", "email", "phone", "last_reading"]

    def get_last_reading(self, obj):
        last = obj.user.vitals.first()  # thanks to ordering = ['-created_at']
        if last:
            return {
                "systolic": last.systolic,
                "diastolic": last.diastolic,
                "heartrate": last.heartrate,
                "created_at": last.created_at,
            }
        return None
        
class PatientSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name  = serializers.CharField(source="user.last_name", read_only=True)
    email      = serializers.EmailField(source="user.email", read_only=True)
    last_reading = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["id", "first_name", "last_name", "email", "phone", "last_reading"]


    def get_last_reading(self, obj):
        last = obj.user.vitals.order_by("-created_at").first()
        if last:
            return {
                "systolic": last.systolic,
                "diastolic": last.diastolic,
                "heartrate": last.heartrate,
                "created_at": last.created_at.strftime("%Y-%m-%d %H:%M")
            }
        return None




class PrescriptionSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = [
            "id",
            "doctor",        # FK to User
            "doctor_name",   # read-only
            "patient",       # FK to UserProfile
            "patient_name",  # read-only
            "medication",
            "dosage",
            "frequency",
            "duration_days",
            "instructions",
            "created_at",
        ]
        read_only_fields = ["id", "doctor", "doctor_name", "created_at"]

    def get_patient_name(self, obj):
        if hasattr(obj.patient, "user") and obj.patient.user:
            return obj.patient.user.get_full_name()
        # fallback to profile fields if available
        if hasattr(obj.patient, "first_name") and hasattr(obj.patient, "last_name"):
            return f"{obj.patient.first_name} {obj.patient.last_name}".strip()
        return f"Patient {obj.patient.id}"

    def get_doctor_name(self, obj):
        if hasattr(obj.doctor, "get_full_name"):
            return obj.doctor.get_full_name()
        if hasattr(obj.doctor, "first_name") and hasattr(obj.doctor, "last_name"):
            return f"{obj.doctor.first_name} {obj.doctor.last_name}".strip()
        return f"Doctor {obj.doctor.id}"
