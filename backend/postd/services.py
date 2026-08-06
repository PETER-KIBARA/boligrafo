from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Any, Mapping

from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.authtoken.models import Token

from .models import Appointment, DoctorProfile, Notification, Prescription, PrescriptionLog, Treatment, UserProfile, VitalReading

User = get_user_model()


class DomainError(Exception):
    """Base domain error raised by the service layer."""

    default_message = "A domain error occurred."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)
        self.message = message or self.default_message


class ValidationDomainError(DomainError):
    default_message = "Invalid request data."


class PermissionDomainError(DomainError):
    default_message = "You are not allowed to perform this action."


class NotFoundDomainError(DomainError):
    default_message = "Requested resource was not found."


class ConflictDomainError(DomainError):
    default_message = "The requested resource already exists."


@dataclass(frozen=True)
class AuthPayload:
    token: str
    user: dict[str, Any]
    doctor: dict[str, Any] | None = None


def _get_doctor_profile(user: Any) -> DoctorProfile:
    doctor_profile = getattr(user, "doctor_profile", None)
    if doctor_profile is None:
        raise PermissionDomainError("Only doctors can perform this action.")
    return doctor_profile


def _get_patient_profile(user: Any) -> UserProfile:
    patient_profile = getattr(user, "profile", None)
    if patient_profile is None:
        raise NotFoundDomainError("User profile not found.")
    return patient_profile


def authenticate_user(*, email: str, password: str, require_doctor_profile: bool = False) -> AuthPayload:
    if not email or not password:
        raise ValidationDomainError("Email and password are required.")

    user = authenticate(username=email, password=password)
    if user is None:
        raise ValidationDomainError("Invalid credentials.")

    if require_doctor_profile and getattr(user, "doctor_profile", None) is None:
        raise PermissionDomainError("Not authorized as doctor.")

    token, _ = Token.objects.get_or_create(user=user)
    user_payload: dict[str, Any] = {
        "id": user.id,
        "name": user.get_full_name() or user.username,
        "email": user.email or "",
    }

    doctor_payload: dict[str, Any] | None = None
    doctor_profile = getattr(user, "doctor_profile", None)
    if doctor_profile is not None:
        doctor_payload = {
            "id": doctor_profile.id,
            "full_name": doctor_profile.full_name,
            "phone": doctor_profile.phone,
            "national_id": doctor_profile.national_id,
            "employee_id": doctor_profile.employee_id,
            "specialty": doctor_profile.specialty,
            "title": doctor_profile.title,
        }

    return AuthPayload(token=token.key, user=user_payload, doctor=doctor_payload)


def logout_user(user: Any) -> None:
    token = getattr(user, "auth_token", None)
    if token is not None:
        token.delete()


@transaction.atomic
def register_patient(doctor_user: Any, payload: Mapping[str, Any]) -> UserProfile:
    doctor_profile = _get_doctor_profile(doctor_user)

    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    confirm_password = str(payload.get("confirm_password", ""))
    name = str(payload.get("name", "")).strip()

    if not email or not password:
        raise ValidationDomainError("Email and password are required.")
    if password != confirm_password:
        raise ValidationDomainError("Passwords do not match.")
    if User.objects.filter(username=email).exists():
        raise ConflictDomainError("Email already registered.")

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=name,
    )

    profile = UserProfile.objects.create(
        user=user,
        phone=payload.get("phone"),
        address=payload.get("address"),
        dob=payload.get("dob") or None,
        gender=payload.get("gender"),
        emergency_name=payload.get("emergency_name"),
        emergency_phone=payload.get("emergency_phone"),
        emergency_relation=payload.get("emergency_relation"),
        doctor=doctor_profile,
    )
    return profile


@transaction.atomic
def create_vital_reading(patient_user: Any, payload: Mapping[str, Any]) -> VitalReading:
    _get_patient_profile(patient_user)

    try:
        return VitalReading.objects.create(
            patient=patient_user,
            systolic=int(payload["systolic"]),
            diastolic=int(payload["diastolic"]),
            heartrate=payload.get("heartrate"),
            symptoms=payload.get("symptoms"),
            diet=payload.get("diet"),
            exercise=payload.get("exercise"),
        )
    except KeyError as exc:
        raise ValidationDomainError(f"Missing field: {exc.args[0]}") from exc
    except (TypeError, ValueError) as exc:
        raise ValidationDomainError("Invalid numeric value for vital reading.") from exc


@transaction.atomic
def create_prescription(doctor_user: Any, payload: Mapping[str, Any]) -> Prescription:
    _get_doctor_profile(doctor_user)
    patient = payload.get("patient")
    if not isinstance(patient, UserProfile):
        raise ValidationDomainError("A valid patient is required.")

    try:
        return Prescription.objects.create(
            doctor=doctor_user,
            patient=patient,
            medication=str(payload["medication"]).strip(),
            dosage=str(payload["dosage"]).strip(),
            frequency=str(payload["frequency"]).strip(),
            duration_days=int(payload["duration_days"]),
            instructions=payload.get("instructions") or "",
        )
    except KeyError as exc:
        raise ValidationDomainError(f"Missing field: {exc.args[0]}") from exc
    except (TypeError, ValueError) as exc:
        raise ValidationDomainError("Invalid prescription payload.") from exc


@transaction.atomic
def update_prescription(prescription: Prescription, doctor_user: Any, payload: Mapping[str, Any]) -> Prescription:
    _get_doctor_profile(doctor_user)
    if not getattr(doctor_user, "is_staff", False) and not getattr(doctor_user, "is_superuser", False) and prescription.doctor_id != doctor_user.id:
        raise PermissionDomainError("You can only update your own prescriptions.")

    mutable_fields = {"medication", "dosage", "frequency", "duration_days", "instructions", "patient"}
    for field_name in mutable_fields:
        if field_name not in payload:
            continue
        value = payload[field_name]
        if field_name == "patient" and value is not None and not isinstance(value, UserProfile):
            raise ValidationDomainError("A valid patient is required.")
        if field_name == "duration_days":
            try:
                value = int(value)
            except (TypeError, ValueError) as exc:
                raise ValidationDomainError("duration_days must be an integer.") from exc
        setattr(prescription, field_name, value)

    prescription.save()
    return prescription


@transaction.atomic
def delete_prescription(prescription: Prescription, doctor_user: Any) -> None:
    _get_doctor_profile(doctor_user)
    if not getattr(doctor_user, "is_staff", False) and not getattr(doctor_user, "is_superuser", False) and prescription.doctor_id != doctor_user.id:
        raise PermissionDomainError("You can only delete your own prescriptions.")
    prescription.delete()


@transaction.atomic
def log_prescription_dose(patient_user: Any, prescription_id: int, dose_label: str) -> tuple[PrescriptionLog, bool]:
    patient_profile = _get_patient_profile(patient_user)
    if dose_label not in {"morning", "afternoon", "evening", "night"}:
        raise ValidationDomainError("Invalid dose_label.")

    try:
        prescription = Prescription.objects.get(id=prescription_id, patient=patient_profile)
    except Prescription.DoesNotExist as exc:
        raise NotFoundDomainError("Prescription not found.") from exc

    today = timezone.localdate()
    start_of_day = datetime.combine(today, time.min, tzinfo=timezone.get_current_timezone())
    end_of_day = datetime.combine(today, time.max, tzinfo=timezone.get_current_timezone())

    log_qs = PrescriptionLog.objects.filter(
        prescription=prescription,
        patient=patient_profile,
        dose_label=dose_label,
        taken_at__range=(start_of_day, end_of_day),
    )

    dose_time_map = {
        "morning": time(8, 0),
        "afternoon": time(14, 0),
        "evening": time(20, 0),
        "night": time(22, 0),
    }
    dose_time = dose_time_map[dose_label]

    if log_qs.exists():
        log = log_qs.select_related("prescription", "patient").first()
        if log is None:
            raise NotFoundDomainError("Prescription log not found.")
        if log.dose_time != dose_time:
            log.dose_time = dose_time
            log.save(update_fields=["dose_time"])
        return log, False

    log = PrescriptionLog.objects.create(
        prescription=prescription,
        patient=patient_profile,
        dose_label=dose_label,
        dose_time=dose_time,
        taken_at=timezone.now(),
    )
    return log, True


@transaction.atomic
def create_treatment(doctor_user: Any, payload: Mapping[str, Any]) -> Treatment:
    _get_doctor_profile(doctor_user)
    patient = payload.get("patient")
    if patient is not None and not isinstance(patient, UserProfile):
        raise ValidationDomainError("A valid patient is required.")

    try:
        return Treatment.objects.create(
            doctor=doctor_user,
            patient=patient,
            name=str(payload["name"]).strip(),
            description=payload.get("description") or "",
            status=str(payload.get("status") or "active"),
        )
    except KeyError as exc:
        raise ValidationDomainError(f"Missing field: {exc.args[0]}") from exc


@transaction.atomic
def update_treatment(treatment: Treatment, doctor_user: Any, payload: Mapping[str, Any]) -> Treatment:
    _get_doctor_profile(doctor_user)
    if not getattr(doctor_user, "is_staff", False) and not getattr(doctor_user, "is_superuser", False) and treatment.doctor_id != doctor_user.id:
        raise PermissionDomainError("You can only update your own treatments.")

    for field_name in ("name", "description", "status", "patient"):
        if field_name not in payload:
            continue
        value = payload[field_name]
        if field_name == "patient" and value is not None and not isinstance(value, UserProfile):
            raise ValidationDomainError("A valid patient is required.")
        setattr(treatment, field_name, value)

    treatment.save()
    return treatment


@transaction.atomic
def delete_treatment(treatment: Treatment, doctor_user: Any) -> None:
    _get_doctor_profile(doctor_user)
    if not getattr(doctor_user, "is_staff", False) and not getattr(doctor_user, "is_superuser", False) and treatment.doctor_id != doctor_user.id:
        raise PermissionDomainError("You can only delete your own treatments.")
    treatment.delete()


@transaction.atomic
def create_appointment(doctor_user: Any, payload: Mapping[str, Any]) -> Appointment:
    doctor_profile = _get_doctor_profile(doctor_user)
    patient = payload.get("patient")
    if not isinstance(patient, UserProfile):
        raise ValidationDomainError("A valid patient is required.")

    try:
        return Appointment.objects.create(
            patient=patient,
            doctor=doctor_profile,
            date=payload.get("date"),
            time=payload.get("time"),
            reason=str(payload.get("reason") or "Hypertension follow-up"),
            status=str(payload.get("status") or "scheduled"),
            created_by=doctor_user,
        )
    except Exception as exc:
        raise ValidationDomainError("Unable to create appointment.") from exc


@transaction.atomic
def update_notification(notification: Notification, payload: Mapping[str, Any]) -> Notification:
    if "is_read" in payload:
        notification.is_read = bool(payload["is_read"])
        notification.save(update_fields=["is_read"])
    return notification


@transaction.atomic
def create_admin_user(*, username: str, email: str, password: str) -> tuple[User, bool]:
    if not username or not email or not password:
        raise ValidationDomainError("username, email and password are required.")

    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email, "is_staff": True, "is_superuser": True},
    )
    if created:
        user.email = email
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user, True

    return user, False


def generate_patient_suggestions(patient: UserProfile) -> list[dict[str, Any]]:
    from .ai.engine import generate_patient_suggestions as _generate_patient_suggestions

    return _generate_patient_suggestions(patient)


def generate_population_insights(population_data: Mapping[str, Any]) -> dict[str, Any]:
    from postd.ai.services.openrouter_service import OpenRouterService

    try:
        return OpenRouterService().generate_population_insights(dict(population_data))
    except Exception as exc:  # pragma: no cover - external dependency failure path
        raise DomainError("Unable to generate population insights.") from exc


class NotificationService:
    @staticmethod
    def check_missed_prescriptions() -> None:
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)

        patient_profiles = UserProfile.objects.select_related("user", "doctor").filter(doctor__isnull=False)

        for patient in patient_profiles:
            today_readings = VitalReading.objects.filter(patient=patient.user, created_at__date=today).exists()
            yesterday_readings = VitalReading.objects.filter(patient=patient.user, created_at__date=yesterday).exists()
            missed_days = int(not today_readings) + int(not yesterday_readings)

            if missed_days < 2:
                continue

            exists_today = Notification.objects.filter(
                doctor=patient.doctor.user,
                patient=patient,
                notification_type="missed_prescription",
                created_at__date=today,
            ).exists()
            if exists_today:
                continue

            Notification.objects.create(
                doctor=patient.doctor.user,
                patient=patient,
                notification_type="missed_prescription",
                title=f"Missed BP Readings - {missed_days} days",
                message=f"{patient.user.get_full_name()} has missed BP readings for {missed_days} consecutive days.",
                missed_days=missed_days,
            )

    @staticmethod
    def check_critical_bp_readings() -> None:
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        critical_readings = VitalReading.objects.select_related("patient__profile", "patient__profile__doctor").filter(
            created_at__gte=twenty_four_hours_ago
        ).filter(
            Q(systolic__gte=180)
            | Q(diastolic__gte=120)
            | Q(systolic__lt=90)
            | Q(diastolic__lt=60)
        )

        for reading in critical_readings:
            patient_profile = getattr(reading.patient, "profile", None)
            if patient_profile is None or patient_profile.doctor is None:
                continue

            if reading.systolic >= 180 or reading.diastolic >= 120:
                bp_category = "Hypertensive Crisis"
            elif reading.systolic < 90 or reading.diastolic < 60:
                bp_category = "Hypotension"
            else:
                bp_category = "Critical Reading"

            exists = Notification.objects.filter(
                doctor=patient_profile.doctor.user,
                patient=patient_profile,
                notification_type="critical_bp",
                bp_systolic=reading.systolic,
                bp_diastolic=reading.diastolic,
                created_at__date=reading.created_at.date(),
            ).exists()
            if exists:
                continue

            Notification.objects.create(
                doctor=patient_profile.doctor.user,
                patient=patient_profile,
                notification_type="critical_bp",
                title=f"Critical BP Reading - {bp_category}",
                message=f"{patient_profile.user.get_full_name()} has a critical BP reading of {reading.systolic}/{reading.diastolic} mmHg ({bp_category}).",
                bp_systolic=reading.systolic,
                bp_diastolic=reading.diastolic,
            )

    @staticmethod
    def generate_all_notifications() -> None:
        NotificationService.check_missed_prescriptions()
        NotificationService.check_critical_bp_readings()
