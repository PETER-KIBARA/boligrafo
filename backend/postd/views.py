from __future__ import annotations

import csv
from datetime import datetime
from typing import Any

from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException, NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import selectors, services
from .models import Appointment, Notification, Prescription, Treatment, UserProfile, VitalReading
from .pdf_report_service import ReportPDFService
from .serializers import (
    AppointmentSerializer,
    AuthLoginSerializer,
    CurrentUserSerializer,
    DoctorProfileSerializer,
    NotificationSerializer,
    PatientSerializer,
    PatientSignupSerializer,
    PrescriptionDoseSerializer,
    PrescriptionSerializer,
    TreatmentSerializer,
    UserProfileSerializer,
    VitalReadingSerializer,
)

class DomainAPIException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "A server error occurred."


def _raise_domain_error(error: services.DomainError) -> None:
    if isinstance(error, services.ValidationDomainError):
        raise ValidationError(detail=error.message)
    if isinstance(error, services.ConflictDomainError):
        raise ValidationError(detail=error.message)
    if isinstance(error, services.NotFoundDomainError):
        raise NotFound(detail=error.message)
    if isinstance(error, services.PermissionDomainError):
        raise PermissionDenied(detail=error.message)
    raise DomainAPIException(detail=error.message)


def _require_doctor_profile(user: Any) -> Any:
    doctor_profile = selectors.get_doctor_profile_for_user(user)
    if doctor_profile is None:
        raise PermissionDenied("Only doctors can access this endpoint.")
    return doctor_profile


def _is_doctor_or_staff(user: Any) -> bool:
    return bool(getattr(user, "is_staff", False) or getattr(user, "is_superuser", False) or selectors.get_doctor_profile_for_user(user) is not None)


def _parse_optional_int(value: Any, field_name: str) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError({field_name: "Must be an integer."}) from exc


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def patient_signup(request: Any) -> Response:
    serializer = PatientSignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        patient_profile = services.register_patient(request.user, serializer.validated_data)
    except services.DomainError as exc:
        _raise_domain_error(exc)

    return Response(
        {
            "message": "Patient registered successfully",
            "patient": UserProfileSerializer(patient_profile, context={"request": request}).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def apilogin(request: Any) -> Response:
    serializer = AuthLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        auth_payload = services.authenticate_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
    except services.DomainError as exc:
        _raise_domain_error(exc)

    return Response(
        {
            "message": "Login successful",
            "token": auth_payload.token,
            "user": auth_payload.user,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request: Any) -> Response:
    serializer = CurrentUserSerializer(
        {
            "id": request.user.id,
            "name": request.user.get_full_name() or request.user.username,
            "email": request.user.email or "",
            "role": selectors.get_current_user_role(request.user),
        }
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def doctor_login(request: Any) -> Response:
    serializer = AuthLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        auth_payload = services.authenticate_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            require_doctor_profile=True,
        )
    except services.DomainError as exc:
        _raise_domain_error(exc)

    return Response(
        {
            "message": "Login successful",
            "token": auth_payload.token,
            "doctor": auth_payload.doctor,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request: Any) -> Response:
    services.logout_user(request.user)
    return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def doctor_patients(request: Any) -> Response:
    doctor_profile = _require_doctor_profile(request.user)
    patients = selectors.get_doctor_patients(doctor_profile, request.query_params.get("q"))
    return Response(UserProfileSerializer(patients, many=True, context={"request": request}).data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def doctor_profile(request: Any) -> Response:
    doctor_profile = _require_doctor_profile(request.user)
    return Response(DoctorProfileSerializer(doctor_profile, context={"request": request}).data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def log_prescription_dose(request: Any, prescription_id: int) -> Response:
    serializer = PrescriptionDoseSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        log, created = services.log_prescription_dose(
            request.user,
            prescription_id,
            serializer.validated_data["dose_label"],
        )
    except services.DomainError as exc:
        _raise_domain_error(exc)

    message = "dose marked as taken" if created else "dose already marked today"
    return Response(
        {"message": f"{serializer.validated_data['dose_label']} {message}", "log_id": log.id},
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


class VitalReadingListCreateView(generics.ListCreateAPIView):
    serializer_class = VitalReadingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        return selectors.get_vital_readings_for_patient(self.request.user)

    def create(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            reading = services.create_vital_reading(request.user, serializer.validated_data)
        except services.DomainError as exc:
            _raise_domain_error(exc)

        output = self.get_serializer(reading)
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)


class DoctorAllPatientsVitalsView(generics.ListAPIView):
    serializer_class = VitalReadingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        doctor_profile = _require_doctor_profile(self.request.user)
        return selectors.get_vital_readings_for_doctor(doctor_profile)


class DoctorVitalReadingListView(generics.ListAPIView):
    serializer_class = VitalReadingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        doctor_profile = _require_doctor_profile(self.request.user)
        patient_id = self.request.query_params.get("patient_id")
        if not patient_id:
            raise ValidationError({"patient_id": "This query parameter is required."})
        return selectors.get_vital_readings_for_doctor(doctor_profile, patient_id=_parse_optional_int(patient_id, "patient_id"))


class DoctorPatientDailyReportsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Any, patient_id: int) -> Response:
        doctor_profile = _require_doctor_profile(request.user)
        patient = get_object_or_404(UserProfile.objects.select_related("user", "doctor"), id=patient_id)
        if not request.user.is_staff and not request.user.is_superuser and patient.doctor_id != doctor_profile.id:
            raise PermissionDenied("You are not authorized to view this patient's report.")

        today = timezone.localdate()
        readings = selectors.get_patient_daily_vital_readings(patient_id, today)
        suggestions = services.generate_patient_suggestions(patient)

        return Response(
            {
                "date": str(today),
                "patient_id": patient.id,
                "readings": VitalReadingSerializer(readings, many=True, context={"request": request}).data,
                "ai_suggestions": suggestions,
            },
            status=status.HTTP_200_OK,
        )


class PatientListView(generics.ListAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        queryset = selectors.get_user_profiles()
        query = self.request.query_params.get("q")
        if query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(user__email__icontains=query)
                | Q(phone__icontains=query)
                | Q(id__icontains=query)
            )
        return queryset


class PrescriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        user = self.request.user
        if _is_doctor_or_staff(user):
            patient_id = self.request.query_params.get("patient_id")
            parsed_patient_id = _parse_optional_int(patient_id, "patient_id")
            return selectors.get_prescriptions_for_doctor(user, patient_id=parsed_patient_id) if parsed_patient_id is not None else selectors.get_prescriptions_for_doctor(user)

        patient_profile = selectors.get_patient_profile_for_user(user)
        if patient_profile is None:
            return Prescription.objects.none()
        return selectors.get_prescriptions_for_patient(patient_profile)

    def create(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            prescription = services.create_prescription(request.user, serializer.validated_data)
        except services.DomainError as exc:
            _raise_domain_error(exc)

        output = self.get_serializer(prescription)
        return Response(output.data, status=status.HTTP_201_CREATED)


class PatientPrescriptionListView(generics.ListAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        patient_profile = selectors.get_patient_profile_for_user(self.request.user)
        if patient_profile is None:
            return Prescription.objects.none()
        return selectors.get_prescriptions_for_patient(patient_profile)


class PrescriptionRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        user = self.request.user
        if _is_doctor_or_staff(user):
            return selectors.get_prescriptions_for_doctor(user)
        patient_profile = selectors.get_patient_profile_for_user(user)
        if patient_profile is None:
            return Prescription.objects.none()
        return selectors.get_prescriptions_for_patient(patient_profile)

    def update(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop("partial", False))
        serializer.is_valid(raise_exception=True)

        try:
            updated = services.update_prescription(instance, request.user, serializer.validated_data)
        except services.DomainError as exc:
            _raise_domain_error(exc)

        return Response(self.get_serializer(updated).data, status=status.HTTP_200_OK)

    def partial_update(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


class PatientPrescriptionRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        patient_profile = selectors.get_patient_profile_for_user(self.request.user)
        if patient_profile is None:
            return Prescription.objects.none()
        return selectors.get_prescriptions_for_patient(patient_profile)

    def update(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        if _is_doctor_or_staff(request.user):
            raise PermissionDenied("Doctors cannot update using this endpoint.")

        serializer = PrescriptionDoseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            log, created = services.log_prescription_dose(
                request.user,
                instance.id,
                serializer.validated_data["dose_label"],
            )
        except services.DomainError as exc:
            _raise_domain_error(exc)

        message = "Dose marked as taken" if created else "Dose already marked today"
        return Response(
            {
                "message": message,
                "log_id": log.id,
                "prescription": self.get_serializer(instance).data,
            },
            status=status.HTTP_200_OK,
        )

    def partial_update(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        return self.update(request, *args, **kwargs)


class TreatmentListCreateView(generics.ListCreateAPIView):
    serializer_class = TreatmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        user = self.request.user
        if _is_doctor_or_staff(user):
            patient_id = self.request.query_params.get("patient_id")
            parsed_patient_id = _parse_optional_int(patient_id, "patient_id")
            return selectors.get_treatments_for_doctor(user, patient_id=parsed_patient_id) if parsed_patient_id is not None else selectors.get_treatments_for_doctor(user)

        patient_profile = selectors.get_patient_profile_for_user(user)
        if patient_profile is None:
            return Treatment.objects.none()
        return selectors.get_treatments_for_patient(patient_profile)

    def create(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            treatment = services.create_treatment(request.user, serializer.validated_data)
        except services.DomainError as exc:
            _raise_domain_error(exc)

        return Response(self.get_serializer(treatment).data, status=status.HTTP_201_CREATED)


class TreatmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TreatmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        user = self.request.user
        if _is_doctor_or_staff(user):
            return selectors.get_treatments_for_doctor(user)
        patient_profile = selectors.get_patient_profile_for_user(user)
        if patient_profile is None:
            return Treatment.objects.none()
        return selectors.get_treatments_for_patient(patient_profile)

    def update(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop("partial", False))
        serializer.is_valid(raise_exception=True)

        try:
            updated = services.update_treatment(instance, request.user, serializer.validated_data)
        except services.DomainError as exc:
            _raise_domain_error(exc)

        return Response(self.get_serializer(updated).data, status=status.HTTP_200_OK)

    def partial_update(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        try:
            services.delete_treatment(instance, request.user)
        except services.DomainError as exc:
            _raise_domain_error(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileListView(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        user_id = _parse_optional_int(self.request.query_params.get("user_id"), "user_id")
        return selectors.get_user_profiles(user_id) if user_id is not None else selectors.get_user_profiles()


class UserProfileDetailView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserProfile.objects.select_related("user", "doctor")
    lookup_field = "id"


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        return selectors.get_notifications_for_user(self.request.user)


class NotificationDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        return selectors.get_notifications_for_user(self.request.user)

    def update(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop("partial", False))
        serializer.is_valid(raise_exception=True)

        try:
            notification = services.update_notification(instance, serializer.validated_data)
        except services.DomainError as exc:
            _raise_domain_error(exc)

        return Response(self.get_serializer(notification).data, status=status.HTTP_200_OK)

    def partial_update(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_admin(request: Any) -> Response:
    if not getattr(request.user, "is_staff", False) and not getattr(request.user, "is_superuser", False):
        raise PermissionDenied("Only administrators can create admin users.")

    username = str(request.data.get("username", "admin")).strip()
    email = str(request.data.get("email", "admin@example.com")).strip()
    password = str(request.data.get("password", "admin123"))

    try:
        user, created = services.create_admin_user(username=username, email=email, password=password)
    except services.DomainError as exc:
        _raise_domain_error(exc)

    return Response(
        {
            "message": "Superuser created ✅" if created else "Admin already exists.",
            "user_id": user.id,
            "created": created,
        },
        status=status.HTTP_200_OK,
    )


class DoctorCreateAppointmentView(generics.CreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            appointment = services.create_appointment(request.user, serializer.validated_data)
        except services.DomainError as exc:
            _raise_domain_error(exc)

        return Response(self.get_serializer(appointment).data, status=status.HTTP_201_CREATED)


class PatientAppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        patient_id = int(self.kwargs["id"])
        if _is_doctor_or_staff(self.request.user):
            return selectors.get_appointments_for_patient_id(patient_id)

        patient_profile = selectors.get_patient_profile_for_user(self.request.user)
        if patient_profile is None or patient_profile.id != patient_id:
            raise PermissionDenied("You are not authorized to view these appointments.")
        return selectors.get_appointments_for_patient(patient_profile)


class PatientMyAppointmentsView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        patient_profile = selectors.get_patient_profile_for_user(self.request.user)
        if patient_profile is None:
            return Appointment.objects.none()
        return selectors.get_appointments_for_patient(patient_profile)


class DoctorUpcomingAppointmentsView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        doctor_profile = _require_doctor_profile(self.request.user)
        return selectors.get_appointments_for_doctor(doctor_profile)


class PopulationBPTrendsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Any) -> Response:
        return Response(selectors.get_population_bp_trends(), status=status.HTTP_200_OK)


class PopulationInsightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Any) -> Response:
        doctor_profile = _require_doctor_profile(request.user)
        population_data = selectors.get_population_insights_summary(doctor_profile)

        try:
            insights_payload = services.generate_population_insights(population_data)
        except services.DomainError as exc:
            _raise_domain_error(exc)

        return Response(
            {
                "summary": population_data,
                "insights": insights_payload.get("insights", []),
                "actions": insights_payload.get("actions", []),
            },
            status=status.HTTP_200_OK,
        )


class DoctorReportGeneratorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Any) -> Response:
        doctor_profile = _require_doctor_profile(request.user)
        patient_id = _parse_optional_int(request.query_params.get("patient_id"), "patient_id")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        patients = selectors.get_doctor_report_patients(doctor_profile, patient_id) if patient_id is not None else selectors.get_doctor_report_patients(doctor_profile)
        report_data = [selectors.get_report_data_for_patient(patient, from_date, to_date) for patient in patients]

        all_systolic = [item["avg_systolic"] for item in report_data if item["avg_systolic"] is not None]
        all_diastolic = [item["avg_diastolic"] for item in report_data if item["avg_diastolic"] is not None]
        all_heartrate = [item["avg_heartrate"] for item in report_data if item["avg_heartrate"] is not None]

        summary = {
            "total_patients": len(report_data),
            "total_vitals": sum(item["total_vitals"] for item in report_data),
            "total_prescriptions": sum(item["total_prescriptions"] for item in report_data),
            "total_treatments": sum(item["total_treatments"] for item in report_data),
            "total_appointments": sum(item["total_appointments"] for item in report_data),
            "avg_systolic": round(sum(all_systolic) / len(all_systolic), 1) if all_systolic else None,
            "avg_diastolic": round(sum(all_diastolic) / len(all_diastolic), 1) if all_diastolic else None,
            "avg_heartrate": round(sum(all_heartrate) / len(all_heartrate), 1) if all_heartrate else None,
            "date_from": from_date,
            "date_to": to_date,
            "patients": report_data,
        }
        return Response(summary, status=status.HTTP_200_OK)


class DoctorReportExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Any) -> HttpResponse:
        doctor_profile = _require_doctor_profile(request.user)
        patient_id = _parse_optional_int(request.query_params.get("patient_id"), "patient_id")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        patients = selectors.get_doctor_report_patients(doctor_profile, patient_id) if patient_id is not None else selectors.get_doctor_report_patients(doctor_profile)

        response = HttpResponse(content_type="text/csv")
        filename = f'patient_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "Patient ID",
                "Patient Name",
                "Patient Email",
                "Patient Phone",
                "Date",
                "Type",
                "Details",
                "Systolic",
                "Diastolic",
                "Heartrate",
                "Medication",
                "Dosage",
                "Frequency",
                "Treatment",
                "Status",
                "Appointment Date",
                "Appointment Time",
                "Reason",
            ]
        )

        for patient in patients:
            report_data = selectors.get_report_data_for_patient(patient, from_date, to_date)
            patient_id_value = report_data["patient_id"]
            patient_name = report_data["patient_name"]
            patient_email = report_data["patient_email"]
            patient_phone = report_data["patient_phone"]

            for vital in report_data["vitals"]:
                writer.writerow(
                    [
                        patient_id_value,
                        patient_name,
                        patient_email,
                        patient_phone,
                        vital["created_at"],
                        "Vital Reading",
                        f"Symptoms: {vital['symptoms'] or 'None'}",
                        vital["systolic"],
                        vital["diastolic"],
                        vital["heartrate"] or "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ]
                )

            for prescription in report_data["prescriptions"]:
                writer.writerow(
                    [
                        patient_id_value,
                        patient_name,
                        patient_email,
                        patient_phone,
                        prescription["created_at"],
                        "Prescription",
                        prescription.get("instructions") or "",
                        "",
                        "",
                        "",
                        prescription["medication"],
                        prescription["dosage"],
                        prescription["frequency"],
                        "",
                        "",
                        "",
                        "",
                        "",
                    ]
                )

            for treatment in report_data["treatments"]:
                writer.writerow(
                    [
                        patient_id_value,
                        patient_name,
                        patient_email,
                        patient_phone,
                        treatment["created_at"],
                        "Treatment",
                        treatment["description"],
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        treatment["name"],
                        treatment["status"],
                        "",
                        "",
                        "",
                    ]
                )

            for appointment in report_data["appointments"]:
                writer.writerow(
                    [
                        patient_id_value,
                        patient_name,
                        patient_email,
                        patient_phone,
                        appointment["created_at"],
                        "Appointment",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        appointment["date"] or "",
                        appointment["time"] or "",
                        appointment["reason"],
                    ]
                )

        return response


class PatientReportPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Any) -> FileResponse:
        patient = selectors.get_patient_profile_for_user(request.user)
        if patient is None:
            raise NotFound("Profile not found.")

        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        report_data = selectors.get_report_data_for_patient(patient, from_date, to_date)
        pdf_buffer = ReportPDFService.generate_patient_report(report_data)

        filename = f"Report_{request.user.username}_{datetime.now().strftime('%Y%m%d')}.pdf"
        return FileResponse(pdf_buffer, as_attachment=True, filename=filename, content_type="application/pdf")


class DoctorPatientReportPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Any, patient_id: int) -> FileResponse:
        doctor_profile = _require_doctor_profile(request.user)
        patient = get_object_or_404(UserProfile.objects.select_related("user", "doctor"), id=patient_id)
        if not request.user.is_staff and not request.user.is_superuser and patient.doctor_id != doctor_profile.id:
            raise PermissionDenied("You are not authorized to view this patient's report.")

        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        report_data = selectors.get_report_data_for_patient(patient, from_date, to_date)
        pdf_buffer = ReportPDFService.generate_patient_report(report_data)

        filename = f"Report_{patient.user.username}_{datetime.now().strftime('%Y%m%d')}.pdf"
        return FileResponse(pdf_buffer, as_attachment=True, filename=filename, content_type="application/pdf")
