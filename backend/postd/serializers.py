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
    class Meta:
        model = UserProfile
        fields = ["id", "first_name", "last_name", "email"]

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "user", "phone", "last_reading_at"]
