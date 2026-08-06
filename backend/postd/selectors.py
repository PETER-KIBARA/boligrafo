from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any, Mapping

from django.contrib.auth import get_user_model
from django.db.models import Avg, Prefetch, Q, QuerySet
from django.utils import timezone

from .models import Appointment, DoctorProfile, Notification, Prescription, PrescriptionLog, Treatment, UserProfile, VitalReading

User = get_user_model()


def _parse_date(value: str | date | None) -> date | None:
    if value is None or isinstance(value, date):
        return value
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _daterange_filters(from_date: str | date | None, to_date: str | date | None, field_name: str = "created_at") -> dict[str, Any]:
    filters: dict[str, Any] = {}
    parsed_from = _parse_date(from_date)
    parsed_to = _parse_date(to_date)

    if parsed_from is not None:
        filters[f"{field_name}__date__gte"] = parsed_from
    if parsed_to is not None:
        filters[f"{field_name}__date__lte"] = parsed_to
    return filters


def get_doctor_profile_for_user(user: Any) -> DoctorProfile | None:
    return getattr(user, "doctor_profile", None)


def get_patient_profile_for_user(user: Any) -> UserProfile | None:
    return getattr(user, "profile", None)


def get_current_user_role(user: Any) -> str:
    if getattr(user, "is_authenticated", False) is False:
        return "anonymous"
    if get_doctor_profile_for_user(user) is not None:
        return "doctor"
    if get_patient_profile_for_user(user) is not None:
        return "patient"
    return "user"


def get_doctor_patients(doctor: DoctorProfile, query: str | None = None) -> QuerySet[UserProfile]:
    queryset = UserProfile.objects.select_related("user", "doctor").prefetch_related(
        Prefetch("user__vitals", queryset=VitalReading.objects.order_by("-created_at"))
    ).filter(doctor=doctor)
    if query:
        queryset = queryset.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(user__email__icontains=query)
            | Q(phone__icontains=query)
            | Q(user__username__icontains=query)
        )
    return queryset.order_by("user__first_name", "user__last_name")


def get_user_profiles(user_id: int | None = None) -> QuerySet[UserProfile]:
    queryset = UserProfile.objects.select_related("user", "doctor").prefetch_related(
        Prefetch("user__vitals", queryset=VitalReading.objects.order_by("-created_at"))
    )
    if user_id is not None:
        queryset = queryset.filter(user_id=user_id)
    return queryset.order_by("user__first_name", "user__last_name")


def get_user_profile_by_id(profile_id: int) -> UserProfile:
    return UserProfile.objects.select_related("user", "doctor").get(id=profile_id)


def get_vital_readings_for_patient(user: Any) -> QuerySet[VitalReading]:
    return VitalReading.objects.select_related("patient").filter(patient=user).order_by("-created_at")


def get_vital_readings_for_doctor(doctor: DoctorProfile | None = None, patient_id: int | None = None) -> QuerySet[VitalReading]:
    queryset = VitalReading.objects.select_related("patient")
    if doctor is not None:
        patient_ids = UserProfile.objects.filter(doctor=doctor).values_list("user_id", flat=True)
        queryset = queryset.filter(patient_id__in=patient_ids)
    if patient_id is not None:
        queryset = queryset.filter(patient_id=patient_id)
    return queryset.order_by("-created_at")


def get_patient_daily_vital_readings(patient_id: int, day: date | None = None) -> QuerySet[VitalReading]:
    target_day = day or timezone.localdate()
    return (
        VitalReading.objects.select_related("patient")
        .filter(patient_id=patient_id, created_at__date=target_day)
        .order_by("-created_at")
    )


def get_prescriptions_for_doctor(doctor_user: Any, patient_id: int | None = None) -> QuerySet[Prescription]:
    queryset = (
        Prescription.objects.select_related("doctor", "patient__user")
        .prefetch_related(Prefetch("logs", queryset=PrescriptionLog.objects.order_by("-taken_at")))
        .order_by("-created_at")
    )
    if patient_id is not None:
        queryset = queryset.filter(patient_id=patient_id)
    if not getattr(doctor_user, "is_staff", False) and not getattr(doctor_user, "is_superuser", False):
        queryset = queryset.filter(doctor=doctor_user)
    return queryset


def get_prescriptions_for_patient(patient_profile: UserProfile) -> QuerySet[Prescription]:
    return (
        Prescription.objects.select_related("doctor", "patient__user")
        .prefetch_related(Prefetch("logs", queryset=PrescriptionLog.objects.order_by("-taken_at")))
        .filter(patient=patient_profile)
        .order_by("-created_at")
    )


def get_prescription_by_id(prescription_id: int) -> Prescription:
    return Prescription.objects.select_related("doctor", "patient__user").prefetch_related(
        Prefetch("logs", queryset=PrescriptionLog.objects.order_by("-taken_at"))
    ).get(id=prescription_id)


def get_treatments_for_doctor(doctor_user: Any, patient_id: int | None = None) -> QuerySet[Treatment]:
    queryset = Treatment.objects.select_related("doctor", "patient__user").order_by("-created_at")
    if patient_id is not None:
        queryset = queryset.filter(patient_id=patient_id)
    if not getattr(doctor_user, "is_staff", False) and not getattr(doctor_user, "is_superuser", False):
        queryset = queryset.filter(doctor=doctor_user)
    return queryset


def get_treatments_for_patient(patient_profile: UserProfile) -> QuerySet[Treatment]:
    return Treatment.objects.select_related("doctor", "patient__user").filter(patient=patient_profile).order_by("-created_at")


def get_notifications_for_user(user: Any) -> QuerySet[Notification]:
    doctor_profile = get_doctor_profile_for_user(user)
    patient_profile = get_patient_profile_for_user(user)

    queryset = Notification.objects.select_related("doctor", "patient__user").order_by("-created_at")
    query = Q()
    if doctor_profile is not None:
        query |= Q(doctor=user)
    if patient_profile is not None:
        query |= Q(patient=patient_profile)
    if not query.children:
        return Notification.objects.none()
    return queryset.filter(query)


def get_appointments_for_patient(patient_profile: UserProfile) -> QuerySet[Appointment]:
    return Appointment.objects.select_related("patient__user", "doctor__user").filter(patient=patient_profile).order_by("-date", "-time")


def get_appointments_for_patient_id(patient_id: int) -> QuerySet[Appointment]:
    return Appointment.objects.select_related("patient__user", "doctor__user").filter(patient_id=patient_id).order_by("-date", "-time")


def get_appointments_for_doctor(doctor_profile: DoctorProfile) -> QuerySet[Appointment]:
    return Appointment.objects.select_related("patient__user", "doctor__user").filter(doctor=doctor_profile).order_by("date", "time")


def get_population_bp_trends() -> list[dict[str, Any]]:
    queryset = (
        VitalReading.objects.values("created_at__date")
        .annotate(
            avg_systolic=Avg("systolic"),
            avg_diastolic=Avg("diastolic"),
            avg_heartrate=Avg("heartrate"),
        )
        .order_by("created_at__date")
    )

    return [
        {
            "date": row["created_at__date"].isoformat(),
            "systolic": round(row["avg_systolic"]),
            "diastolic": round(row["avg_diastolic"]),
            "heartrate": round(row["avg_heartrate"]) if row["avg_heartrate"] is not None else None,
        }
        for row in queryset
    ]


def get_population_insights_summary(doctor_profile: DoctorProfile) -> dict[str, Any]:
    patient_queryset = UserProfile.objects.filter(doctor=doctor_profile).select_related("user")
    patient_ids = patient_queryset.values_list("user_id", flat=True)
    vitals_qs = VitalReading.objects.filter(patient_id__in=patient_ids)

    stats = vitals_qs.aggregate(
        avg_systolic=Avg("systolic"),
        avg_diastolic=Avg("diastolic"),
        avg_heartrate=Avg("heartrate"),
    )

    uncontrolled_count = vitals_qs.filter(Q(systolic__gte=140) | Q(diastolic__gte=90)).values("patient_id").distinct().count()
    seven_days_ago = timezone.now() - timedelta(days=7)
    trends = (
        vitals_qs.filter(created_at__gte=seven_days_ago)
        .values("created_at__date")
        .annotate(avg_systolic=Avg("systolic"), avg_diastolic=Avg("diastolic"))
        .order_by("created_at__date")
    )

    return {
        "total_patients": patient_queryset.count(),
        "avg_systolic": round(stats["avg_systolic"], 1) if stats["avg_systolic"] is not None else None,
        "avg_diastolic": round(stats["avg_diastolic"], 1) if stats["avg_diastolic"] is not None else None,
        "avg_heartrate": round(stats["avg_heartrate"], 1) if stats["avg_heartrate"] is not None else None,
        "uncontrolled_count": uncontrolled_count,
        "trends": [
            {
                "date": row["created_at__date"].isoformat(),
                "systolic": round(row["avg_systolic"]),
                "diastolic": round(row["avg_diastolic"]),
            }
            for row in trends
        ],
    }


def get_doctor_report_patients(doctor_profile: DoctorProfile, patient_id: int | None = None) -> QuerySet[UserProfile]:
    queryset = UserProfile.objects.select_related("user", "doctor").filter(doctor=doctor_profile)
    if patient_id is not None:
        queryset = queryset.filter(id=patient_id)
    return queryset.order_by("user__first_name", "user__last_name")


def get_report_data_for_patient(patient: UserProfile, from_date: str | date | None = None, to_date: str | date | None = None) -> dict[str, Any]:
    date_filters = _daterange_filters(from_date, to_date)
    appointment_filters = _daterange_filters(from_date, to_date, field_name="date")

    vitals = VitalReading.objects.filter(patient=patient.user, **date_filters).order_by("-created_at")
    prescriptions = Prescription.objects.select_related("doctor").filter(patient=patient, **date_filters).order_by("-created_at")
    treatments = Treatment.objects.select_related("doctor").filter(patient=patient, **date_filters).order_by("-created_at")
    appointments = Appointment.objects.select_related("doctor").filter(patient=patient, **appointment_filters).order_by("-date", "-time")

    vitals_stats = vitals.aggregate(
        avg_systolic=Avg("systolic"),
        avg_diastolic=Avg("diastolic"),
        avg_heartrate=Avg("heartrate"),
    )

    return {
        "patient_id": patient.id,
        "patient_name": patient.user.get_full_name() or patient.user.username,
        "patient_email": patient.user.email,
        "patient_phone": patient.phone or "",
        "total_vitals": vitals.count(),
        "total_prescriptions": prescriptions.count(),
        "total_treatments": treatments.count(),
        "total_appointments": appointments.count(),
        "avg_systolic": round(vitals_stats["avg_systolic"], 1) if vitals_stats["avg_systolic"] is not None else None,
        "avg_diastolic": round(vitals_stats["avg_diastolic"], 1) if vitals_stats["avg_diastolic"] is not None else None,
        "avg_heartrate": round(vitals_stats["avg_heartrate"], 1) if vitals_stats["avg_heartrate"] is not None else None,
        "vitals": [
            {
                "id": reading.id,
                "systolic": reading.systolic,
                "diastolic": reading.diastolic,
                "heartrate": reading.heartrate,
                "symptoms": reading.symptoms,
                "diet": reading.diet,
                "exercise": reading.exercise,
                "created_at": reading.created_at.isoformat(),
            }
            for reading in vitals
        ],
        "prescriptions": [
            {
                "id": prescription.id,
                "medication": prescription.medication,
                "dosage": prescription.dosage,
                "frequency": prescription.frequency,
                "duration_days": prescription.duration_days,
                "instructions": prescription.instructions,
                "doctor_name": prescription.doctor.get_full_name() if hasattr(prescription.doctor, "get_full_name") else "N/A",
                "created_at": prescription.created_at.isoformat(),
            }
            for prescription in prescriptions
        ],
        "treatments": [
            {
                "id": treatment.id,
                "name": treatment.name,
                "description": treatment.description,
                "status": treatment.status,
                "doctor_name": treatment.doctor.get_full_name() if hasattr(treatment.doctor, "get_full_name") else "N/A",
                "created_at": treatment.created_at.isoformat(),
                "updated_at": treatment.updated_at.isoformat(),
            }
            for treatment in treatments
        ],
        "appointments": [
            {
                "id": appointment.id,
                "date": appointment.date.isoformat() if appointment.date else None,
                "time": appointment.time.isoformat() if appointment.time else None,
                "reason": appointment.reason,
                "status": appointment.status,
                "doctor_name": appointment.doctor.full_name if appointment.doctor else "",
                "created_at": appointment.created_at.isoformat(),
            }
            for appointment in appointments
        ],
    }
