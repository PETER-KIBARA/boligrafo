from rest_framework import serializers
from  .models import UserProfile
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from .models import DoctorProfile
from .models import VitalReading



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

    class Meta:
        model = DoctorProfile
        fields = [
            "id", "full_name", "phone", "national_id",
            "employee_id", "specialty", "title", "email", "username"
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
    user = UserSerializer(read_only=True)
    last_reading = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["id", "user", "phone", "last_reading"]

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
