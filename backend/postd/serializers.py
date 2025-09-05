from rest_framework import serializers
from  .models import UserProfile
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from .models import DoctorProfile



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



class DoctorProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            "id", "full_name", "phone", "national_id",
            "employee_id", "specialty", "title", "email", "username"
        ]

        

