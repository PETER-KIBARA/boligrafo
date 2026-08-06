from __future__ import annotations

from datetime import datetime, time
from typing import Any

from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import Appointment, DoctorProfile, Notification, Prescription, PrescriptionLog, Treatment, UserProfile, VitalReading

User = get_user_model()


class AuthLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        email = attrs.get("email")
        password = attrs.get("password")
        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")
        return attrs


class PatientSignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    dob = serializers.DateField(required=False, allow_null=True)
    gender = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    emergency_name = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    emergency_phone = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    emergency_relation = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    confirm_password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs


class CurrentUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.EmailField(allow_blank=True)
    role = serializers.CharField()


class DoctorProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfile
        fields = [
            "id",
            "full_name",
            "phone",
            "national_id",
            "employee_id",
            "specialty",
            "title",
            "email",
            "username",
            "profile_picture",
            "profile_picture_url",
        ]
        read_only_fields = fields

    def get_profile_picture_url(self, obj: DoctorProfile) -> str | None:
        if not obj.profile_picture:
            return None
        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(obj.profile_picture.url)
        return obj.profile_picture.url


class UserProfileSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(source="user.id", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="user.email", read_only=True)
    doctor_id = serializers.IntegerField(source="doctor.id", read_only=True)
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "patient_id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "address",
            "dob",
            "gender",
            "emergency_name",
            "emergency_phone",
            "emergency_relation",
            "doctor_id",
            "doctor_name",
        ]
        read_only_fields = fields

    def get_full_name(self, obj: UserProfile) -> str:
        return obj.user.get_full_name() or obj.user.username

    def get_doctor_name(self, obj: UserProfile) -> str | None:
        if obj.doctor is None:
            return None
        return obj.doctor.full_name


class PatientSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(source="user.id", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    last_reading = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["patient_id", "id", "first_name", "last_name", "email", "phone", "last_reading"]
        read_only_fields = fields

    def get_last_reading(self, obj: UserProfile) -> dict[str, Any] | None:
        vitals = list(obj.user.vitals.all())
        if not vitals:
            return None
        last = vitals[0]
        return {
            "systolic": last.systolic,
            "diastolic": last.diastolic,
            "heartrate": last.heartrate,
            "created_at": last.created_at.strftime("%Y-%m-%d %H:%M"),
        }


class VitalReadingSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    patient_email = serializers.SerializerMethodField()

    class Meta:
        model = VitalReading
        fields = [
            "id",
            "patient",
            "patient_name",
            "patient_email",
            "systolic",
            "diastolic",
            "heartrate",
            "symptoms",
            "diet",
            "exercise",
            "created_at",
        ]
        read_only_fields = ["id", "patient", "patient_name", "patient_email", "created_at"]

    def get_patient_name(self, obj: VitalReading) -> str:
        return obj.patient.get_full_name() or obj.patient.username

    def get_patient_email(self, obj: VitalReading) -> str:
        return obj.patient.email or ""


class PrescriptionSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    doses_taken_today = serializers.SerializerMethodField()
    remaining_doses = serializers.SerializerMethodField()
    patient = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.select_related("user", "doctor"))

    class Meta:
        model = Prescription
        fields = [
            "id",
            "doctor",
            "doctor_name",
            "patient",
            "patient_name",
            "medication",
            "dosage",
            "frequency",
            "duration_days",
            "instructions",
            "created_at",
            "doses_taken_today",
            "remaining_doses",
        ]
        read_only_fields = ["id", "doctor", "doctor_name", "created_at", "patient_name", "doses_taken_today", "remaining_doses"]

    def get_patient_name(self, obj: Prescription) -> str:
        return obj.patient.user.get_full_name() or obj.patient.user.username

    def get_doctor_name(self, obj: Prescription) -> str:
        return obj.doctor.get_full_name() or obj.doctor.username

    def _taken_dose_labels(self, obj: Prescription) -> list[str]:
        today = timezone.localdate()
        logs = getattr(obj, "logs", None)
        if logs is None:
            return [log.dose_label for log in obj.logs.filter(taken_at__date=today)]
        today_logs = [log for log in logs.all() if log.taken_at.date() == today]
        return [log.dose_label for log in today_logs]

    def get_doses_taken_today(self, obj: Prescription) -> list[str]:
        today = timezone.localdate()
        logs = list(obj.logs.all())
        return [log.dose_label for log in logs if log.taken_at.date() == today]

    def get_remaining_doses(self, obj: Prescription) -> list[str]:
        dose_map = {
            "1": ["morning"],
            "2": ["morning", "evening"],
            "3": ["morning", "afternoon", "evening"],
            "4": ["morning", "afternoon", "evening", "night"],
        }
        expected = dose_map.get(str(obj.frequency), [])
        taken = set(self.get_doses_taken_today(obj))
        return [dose for dose in expected if dose not in taken]


class PrescriptionDoseSerializer(serializers.Serializer):
    taken_today = serializers.BooleanField(required=False, default=True)
    dose_label = serializers.ChoiceField(choices=["morning", "afternoon", "evening", "night"])


class TreatmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    patient = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.select_related("user", "doctor"), required=False, allow_null=True)

    class Meta:
        model = Treatment
        fields = [
            "id",
            "doctor",
            "doctor_name",
            "patient",
            "patient_name",
            "name",
            "description",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "doctor", "doctor_name", "patient_name", "created_at", "updated_at"]

    def get_doctor_name(self, obj: Treatment) -> str:
        return obj.doctor.get_full_name() or obj.doctor.username

    def get_patient_name(self, obj: Treatment) -> str | None:
        if obj.patient is None:
            return None
        return obj.patient.user.get_full_name() or obj.patient.user.username


class NotificationSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    patient_email = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    bp_status = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "is_read",
            "created_at",
            "created_at_formatted",
            "bp_systolic",
            "bp_diastolic",
            "bp_status",
            "patient_name",
            "patient_email",
            "doctor_name",
        ]
        read_only_fields = ["id", "created_at", "created_at_formatted", "bp_status", "patient_name", "patient_email", "doctor_name"]

    def get_patient_name(self, obj: Notification) -> str | None:
        if obj.patient is None:
            return None
        return obj.patient.user.get_full_name() or obj.patient.user.username

    def get_patient_email(self, obj: Notification) -> str | None:
        if obj.patient is None:
            return None
        return obj.patient.user.email or ""

    def get_doctor_name(self, obj: Notification) -> str:
        return obj.doctor.get_full_name() or obj.doctor.username

    def get_created_at_formatted(self, obj: Notification) -> str:
        return obj.created_at.strftime("%Y-%m-%d %H:%M")

    def get_bp_status(self, obj: Notification) -> str | None:
        if obj.bp_systolic is None or obj.bp_diastolic is None:
            return None
        if obj.bp_systolic >= 180 or obj.bp_diastolic >= 120:
            return "Hypertensive Crisis"
        if obj.bp_systolic >= 140 or obj.bp_diastolic >= 90:
            return "Stage 2 Hypertension"
        if obj.bp_systolic >= 130 or obj.bp_diastolic >= 80:
            return "Stage 1 Hypertension"
        if obj.bp_systolic < 90 or obj.bp_diastolic < 60:
            return "Hypotension"
        return "Normal"


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    patient = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.select_related("user", "doctor"))
    doctor = serializers.PrimaryKeyRelatedField(queryset=DoctorProfile.objects.select_related("user"), required=False, allow_null=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "patient_name",
            "doctor",
            "doctor_name",
            "date",
            "time",
            "reason",
            "status",
            "created_at",
            "created_by",
        ]
        read_only_fields = ["id", "patient_name", "doctor_name", "created_at", "created_by"]

    def get_patient_name(self, obj: Appointment) -> str:
        return obj.patient.user.get_full_name() or obj.patient.user.username

    def get_doctor_name(self, obj: Appointment) -> str | None:
        if obj.doctor is None:
            return None
        return obj.doctor.full_name
