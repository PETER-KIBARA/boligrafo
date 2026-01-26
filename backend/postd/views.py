from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from postd.models import UserProfile  
from postd.serializers import UserProfileSerializer
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from postd.models import DoctorProfile  
from django.db import transaction
from postd.serializers import DoctorProfileSerializer
from rest_framework import generics, permissions
from django.db.models import Q
from .models import VitalReading
from .serializers import VitalReadingSerializer
from rest_framework import filters
from .serializers import PatientSerializer
from .models import Prescription
from .serializers import PrescriptionSerializer
from .models import UserProfile  
from .models import Treatment
from .models import PrescriptionLog
from datetime import datetime, time
from .serializers import TreatmentSerializer
from .serializers import UserProfileSerializer
from .models import Notification
from .serializers import NotificationSerializer
from .services import NotificationService
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from .models import Appointment
from rest_framework import serializers
from .serializers import AppointmentSerializer
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.http import FileResponse
from .pdf_report_service import ReportPDFService

@api_view(["POST"])
@permission_classes([IsAuthenticated])  
def patient_signup(request):
    data = request.data
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    if password != confirm_password:
        return Response({"error": "Passwords do not match"}, status=400)


    if User.objects.filter(username=data.get("email")).exists():
        return Response({"error": "Email already registered"}, status=400)

    try:
        with transaction.atomic():
            
            user = User.objects.create_user(
                username=data.get("email"),
                email=data.get("email"),
                password=password,
                first_name=data.get("name"),
            )

            
            profile = UserProfile.objects.create(
                user=user,
                phone=data.get("phone"),
                address=data.get("address"),
                dob=data.get("dob") or None,
                gender=data.get("gender"),
                emergency_name=data.get("emergency_name"),
                emergency_phone=data.get("emergency_phone"),
                emergency_relation=data.get("emergency_relation"),
                doctor=request.user.doctor_profile,  
            )

        return Response({"message": "Patient registered successfully"}, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def apilogin(request):
    data = request.data
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return Response({"error": "Email and password are required"}, status=400)

    # Authenticate using Django
    user = authenticate(username=email, password=password)

    if user is None:
        return Response({"error": "Invalid credentials"}, status=401)

    token, created = Token.objects.get_or_create(user=user)

    return Response({
    "message": "Login successful",
    "token": token.key,
    "user": {
        "id": user.id,
        "name": user.first_name or "",
        "email": user.email or "",
    }
}, status=200)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Return basic info for the currently logged-in user.
    """
    user = request.user
    role = "patient"
    if hasattr(user, "doctor_profile"):
        role = "doctor"
    
    return Response({
        "id": user.id,
        "name": user.get_full_name() or user.username,
        "email": user.email,
        "role": role,
    })

@api_view(["POST"])
@permission_classes([AllowAny])
def doctor_login(request):
    """
    Doctor Login API
    """
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Email and password are required"}, status=400)

    user = authenticate(username=email, password=password)
    if user is None:
        return Response({"error": "Invalid credentials"}, status=400)

    
    if not hasattr(user, "doctor_profile"):
        return Response({"error": "Not authorized as doctor"}, status=403)

    
    token, _ = Token.objects.get_or_create(user=user)
    doctor = user.doctor_profile

    serializer = DoctorProfileSerializer(doctor)
    return Response({
        "message": "Login successful",
        "token": token.key,
        "doctor": serializer.data
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    request.user.auth_token.delete()
    return Response({"message": "Logged out successfully."}, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def doctor_patients(request):
    """
    Fetch patients assigned to the logged-in doctor
    """
    
    if not hasattr(request.user, "doctor_profile"):
        return Response({"error": "Not authorized"}, status=403)

    doctor = request.user.doctor_profile
    patients = UserProfile.objects.filter(doctor=doctor)  

    serializer = UserProfileSerializer(patients, many=True)
    return Response(serializer.data, status=200)

    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def doctor_profile(request):
    """
    Return logged-in doctor's profile info including profile picture
    """
    if not hasattr(request.user, "doctor_profile"):
        return Response({"error": "Not authorized"}, status=403)

    doctor = request.user.doctor_profile
    profile_pic_url = (
        request.build_absolute_uri(doctor.profile_picture.url)
        if doctor.profile_picture
        else None
    )
    serializer = DoctorProfileSerializer(doctor, context={"request": request})


    data = {
        "id": doctor.id,
        "full_name": doctor.full_name,
        "email": request.user.email,
        "username": request.user.username,
        "phone": doctor.phone,
        "national_id": doctor.national_id,
        "specialty": doctor.specialty,
        "employee_id": doctor.employee_id,
        "title": doctor.title,
        "profile_picture": profile_pic_url,
    }

    return Response(data, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def log_prescription_dose(request, prescription_id):
    """
    Endpoint for patients to mark a dose as taken.
    """
    user = request.user
    profile = getattr(user, "profile", None)
    if not profile:
        return Response({"error": "User profile not found"}, status=404)

    try:
        prescription = Prescription.objects.get(id=prescription_id, patient=profile)
    except Prescription.DoesNotExist:
        return Response({"error": "Prescription not found"}, status=404)

    dose_label = request.data.get("dose_label")
    if dose_label not in ["morning", "afternoon", "evening", "night"]:
        return Response({"error": "Invalid dose_label"}, status=400)

    today = timezone.localdate()
    start_of_day = datetime.combine(today, time.min, tzinfo=timezone.get_current_timezone())
    end_of_day = datetime.combine(today, time.max, tzinfo=timezone.get_current_timezone())

    log_exists = PrescriptionLog.objects.filter(
        prescription=prescription,
        patient=profile,
        dose_label=dose_label,
        taken_at__range=(start_of_day, end_of_day)
    ).exists()

    if log_exists:
        return Response({"message": f"{dose_label} dose already marked today"}, status=200)

    # Map dose_label to approximate time
    dose_time_map = {
        "morning": time(8, 0),
        "afternoon": time(14, 0),
        "evening": time(20, 0),
        "night": time(22, 0),
    }

    PrescriptionLog.objects.create(
        prescription=prescription,
        patient=profile,
        dose_label=dose_label,
        dose_time=dose_time_map.get(dose_label, timezone.now().time()),
        taken_at=timezone.now()
    )

    return Response({"message": f"{dose_label} dose marked as taken"}, status=201)

def get_remaining_doses(self, obj):
    freq_map = {"1": ["morning"], "2": ["morning", "evening"], "3": ["morning", "afternoon", "evening"]}
    today_logs = obj.logs.filter(taken_at__date=timezone.localdate())
    taken_labels = [log.dose_label for log in today_logs]
    all_labels = freq_map.get(str(obj.frequency), [])
    return list(set(all_labels) - set(taken_labels))



class VitalReadingListCreateView(generics.ListCreateAPIView):
    serializer_class = VitalReadingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VitalReading.objects.filter(patient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

# Add this to your views.py
class DoctorAllPatientsVitalsView(generics.ListAPIView):
    serializer_class = VitalReadingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        is_doctor = (
            user.is_staff or 
            user.is_superuser or 
            hasattr(user, 'doctor')
        )
        
        if not is_doctor:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only doctors can access this endpoint")
        
        # Get all patients for this doctor and their vitals
        if hasattr(user, 'doctor'):
            patient_ids = user.doctor.patients.values_list('id', flat=True)
            return VitalReading.objects.filter(patient_id__in=patient_ids).order_by('-created_at')
        else:
            return VitalReading.objects.all().order_by('-created_at')

class DoctorVitalReadingListView(generics.ListAPIView):
    serializer_class = VitalReadingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # More flexible doctor check
        user = self.request.user
        
        # Check if user is staff (common for doctors)
        # OR has doctor profile
        # OR is superuser
        is_doctor = (
            user.is_staff or 
            user.is_superuser or 
            hasattr(user, 'doctor')  # If you have a Doctor profile model
        )
        
        if not is_doctor:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only doctors can access this endpoint")
        
        patient_id = self.request.query_params.get('patient_id')
        if not patient_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("patient_id parameter is required")
        
        # Doctors can view any patient's vitals
        return VitalReading.objects.filter(patient_id=patient_id).order_by('-created_at')

class DoctorPatientDailyReportsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        # Ensure only doctors can access
        if not hasattr(request.user, "doctor_profile"):
            return Response({"error": "Not authorized"}, status=403)

        today = timezone.now().date()
        readings = VitalReading.objects.filter(patient_id=patient_id, created_at__date=today).order_by('-created_at')

        serializer = VitalReadingSerializer(readings, many=True)
        return Response({
            "date": str(today),
            "readings": serializer.data
        })
    def get(self, request, patient_id):
        patient = get_object_or_404(UserProfile, id=patient_id)

        suggestions = generate_patient_suggestions(patient)

        return JsonResponse({
            "patient_id": patient.id,
            "ai_suggestions": suggestions
        })

class PatientListView(generics.ListAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserProfile.objects.all().select_related("user")
    filter_backends = [filters.SearchFilter]
    search_fields = ["user__first_name", "user__last_name", "phone", "id"]

    def get_queryset(self):
        qs = UserProfile.objects.select_related("user").all()
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(user__email__icontains=q) |
                Q(phone__icontains=q) |
                Q(id__icontains=q)
            )
        return qs




class PrescriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        patient_id = self.request.query_params.get("patient_id")

        if hasattr(user, "doctor_profile"):
            qs = Prescription.objects.all()
            if patient_id:
                qs = qs.filter(patient_id=patient_id)
            return qs.order_by("-created_at")

        # If patient is logged in (linked through UserProfile)
        if hasattr(user, "userprofile"):
            return Prescription.objects.filter(patient=user.userprofile).order_by("-created_at")

        return Prescription.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, "doctor_profile"):
            serializer.save(doctor=user)
        else:
            raise PermissionDenied("Only doctors can create prescriptions.")



class PatientPrescriptionListView(generics.ListAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        profile = getattr(user, "profile", None)

        if not profile:
            return Prescription.objects.none()

        return Prescription.objects.filter(patient=profile).order_by("-created_at")

        
class PrescriptionRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user
        if not hasattr(user, "doctor_profile"):
            raise PermissionDenied("Only doctors can update prescriptions.")
        serializer.save(doctor=user)  # FIXED LINE





class PatientPrescriptionRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        profile = getattr(user, "profile", None)
        if profile is None:
            return Prescription.objects.none()
        return Prescription.objects.filter(patient=profile)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        user = request.user
        if hasattr(user, "doctor_profile"):
            raise PermissionDenied("Doctors cannot update using this endpoint.")

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Handle dose logging
        taken_today = request.data.get("taken_today")
        dose_label = request.data.get("dose_label")

        if taken_today and dose_label:
            self.log_dose(instance, dose_label)

        return Response(serializer.data)

    def log_dose(self, prescription, dose_label):
        user = self.request.user
        profile = getattr(user, "profile", None)
        if profile is None:
            return

        # Map dose_label to actual time (timezone-aware)
        dose_time_map = {
            "morning": time(8, 0),
            "afternoon": time(14, 0),
            "evening": time(20, 0),
            "night": time(22, 0),
        }
        dose_time = dose_time_map.get(dose_label, timezone.now().time())

        today = timezone.localdate()
        start_of_day = datetime.combine(today, time.min, tzinfo=timezone.get_current_timezone())
        end_of_day = datetime.combine(today, time.max, tzinfo=timezone.get_current_timezone())

        log_qs = PrescriptionLog.objects.filter(
            prescription=prescription,
            patient=profile,
            dose_label=dose_label,
            taken_at__range=(start_of_day, end_of_day)
        )

        if log_qs.exists():
            log = log_qs.first()
            log.dose_time = dose_time
            log.save()
        else:
            PrescriptionLog.objects.create(
                prescription=prescription,
                patient=profile,
                dose_label=dose_label,
                taken_at=timezone.now(),
                dose_time=dose_time
            )



class TreatmentListCreateView(generics.ListCreateAPIView):
    serializer_class = TreatmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Treatment.objects.all()

    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user)


class TreatmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TreatmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Treatment.objects.all()



class UserProfileListView(generics.ListAPIView):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        queryset = UserProfile.objects.all()
        user_id = self.request.query_params.get("user_id")
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset


class UserProfileDetailView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserProfile.objects.all()
    lookup_field = 'id'




class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Check if this user is a doctor or patient
        doctor_profile = DoctorProfile.objects.filter(user=user).first()
        patient_profile = UserProfile.objects.filter(user=user).first()

        query = Q()

        if doctor_profile:
            # doctor field expects a User instance, not DoctorProfile
            query |= Q(doctor=user)
        if patient_profile:
            # patient field expects a UserProfile instance
            query |= Q(patient=patient_profile)

        return Notification.objects.filter(query).order_by('-created_at')

class NotificationDetailView(generics.RetrieveUpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_update(self, serializer):
        # Only allow updating is_read field
        serializer.save()



from django.contrib.auth import get_user_model
from django.http import HttpResponse

def create_admin(request):
    User = get_user_model()
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@example.com", "admin123")
        return HttpResponse("Superuser created ✅")
    else:
        return HttpResponse("Admin already exists.")

class DoctorCreateAppointmentView(generics.CreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, "doctor_profile"):
            raise PermissionDenied("Only doctors can schedule follow-up appointments.")
        
        serializer.save(
            doctor=user.doctor_profile,
            created_by=user
        )

class PatientAppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        patient_id = self.kwargs["id"]
        return Appointment.objects.filter(patient_id=patient_id).order_by("-date")

class PatientMyAppointmentsView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Appointment.objects.filter(patient=user.profile).order_by("date")


class DoctorUpcomingAppointmentsView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Appointment.objects.filter(
            doctor=user.doctor_profile
        ).order_by("date", "time")
    
class PopulationBPTrendsView(APIView):
    permission_classes = []  # or IsAuthenticated

    def get(self, request):
        qs = (
            VitalReading.objects
            .values("created_at__date")
            .annotate(
                avg_systolic=Avg("systolic"),
                avg_diastolic=Avg("diastolic"),
                avg_heartrate=Avg("heartrate"),
            )
            .order_by("created_at__date")
        )

        data = [
            {
                "date": row["created_at__date"].isoformat(),
                "systolic": round(row["avg_systolic"]),
                "diastolic": round(row["avg_diastolic"]),
                "heartrate": round(row["avg_heartrate"]) if row["avg_heartrate"] else None,
            }
            for row in qs
        ]

        return JsonResponse(data, safe=False)


from postd.ai.services.openrouter_service import OpenRouterService

class PopulationInsightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, "doctor_profile"):
            return Response({"error": "Only doctors can access population insights."}, status=403)

        doctor = request.user.doctor_profile
        patients = UserProfile.objects.filter(doctor=doctor)
        patient_ids = patients.values_list('user_id', flat=True)

        vitals_qs = VitalReading.objects.filter(patient_id__in=patient_ids)
        
        # Calculate stats
        stats = vitals_qs.aggregate(
            avg_systolic=Avg('systolic'),
            avg_diastolic=Avg('diastolic'),
            avg_heartrate=Avg('heartrate')
        )

        uncontrolled_count = vitals_qs.filter(
            Q(systolic__gte=140) | Q(diastolic__gte=90)
        ).values('patient_id').distinct().count()

        # Get trends (last 7 days grouped by date)
        seven_days_ago = timezone.now() - timedelta(days=7)
        trends_qs = (
            vitals_qs.filter(created_at__gte=seven_days_ago)
            .values("created_at__date")
            .annotate(
                avg_systolic=Avg("systolic"),
                avg_diastolic=Avg("diastolic"),
            )
            .order_by("created_at__date")
        )
        
        trends = [
            {
                "date": row["created_at__date"].isoformat(),
                "systolic": round(row["avg_systolic"]),
                "diastolic": round(row["avg_diastolic"]),
            }
            for row in trends_qs
        ]

        population_data = {
            "total_patients": patients.count(),
            "avg_systolic": round(stats['avg_systolic'], 1) if stats['avg_systolic'] else None,
            "avg_diastolic": round(stats['avg_diastolic'], 1) if stats['avg_diastolic'] else None,
            "avg_heartrate": round(stats['avg_heartrate'], 1) if stats['avg_heartrate'] else None,
            "uncontrolled_count": uncontrolled_count,
            "trends": trends
        }

        ai_service = OpenRouterService()
        insights = ai_service.generate_population_insights(population_data)

        return Response({
            "summary": population_data,
            "insights": insights.get("insights", []),
            "actions": insights.get("actions", [])
        })


class DoctorReportGeneratorView(APIView):
    """
    Generate comprehensive reports for doctor's patients
    Query params: patient_id (optional), from_date (optional), to_date (optional)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Ensure only doctors can access
        if not hasattr(request.user, "doctor_profile"):
            return Response({"error": "Not authorized"}, status=403)

        doctor = request.user.doctor_profile
        
        # Get query parameters
        patient_id = request.query_params.get('patient_id')
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        # Get doctor's patients
        patients_qs = UserProfile.objects.filter(doctor=doctor)
        
        # Filter by specific patient if provided
        if patient_id:
            patients_qs = patients_qs.filter(id=patient_id)

        report_data = []
        
        for patient in patients_qs:
            patient_data = get_report_data_for_patient(patient, from_date, to_date)
            report_data.append(patient_data)

        # Calculate overall statistics
        total_vitals = sum(p['total_vitals'] for p in report_data)
        total_prescriptions = sum(p['total_prescriptions'] for p in report_data)
        total_treatments = sum(p['total_treatments'] for p in report_data)
        total_appointments = sum(p['total_appointments'] for p in report_data)
        
        # Calculate overall averages
        all_systolic = [p['avg_systolic'] for p in report_data if p['avg_systolic']]
        all_diastolic = [p['avg_diastolic'] for p in report_data if p['avg_diastolic']]
        all_heartrate = [p['avg_heartrate'] for p in report_data if p['avg_heartrate']]

        summary = {
            'total_patients': len(report_data),
            'total_vitals': total_vitals,
            'total_prescriptions': total_prescriptions,
            'total_treatments': total_treatments,
            'total_appointments': total_appointments,
            'avg_systolic': round(sum(all_systolic) / len(all_systolic), 1) if all_systolic else None,
            'avg_diastolic': round(sum(all_diastolic) / len(all_diastolic), 1) if all_diastolic else None,
            'avg_heartrate': round(sum(all_heartrate) / len(all_heartrate), 1) if all_heartrate else None,
            'date_from': from_date,
            'date_to': to_date,
            'patients': report_data
        }

        return Response(summary)


import csv
from django.http import HttpResponse

class DoctorReportExportView(APIView):
    """
    Export reports as CSV
    Query params: patient_id (optional), from_date (optional), to_date (optional)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Ensure only doctors can access
        if not hasattr(request.user, "doctor_profile"):
            return Response({"error": "Not authorized"}, status=403)

        doctor = request.user.doctor_profile
        
        # Get query parameters
        patient_id = request.query_params.get('patient_id')
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        # Get doctor's patients
        patients_qs = UserProfile.objects.filter(doctor=doctor)
        
        # Filter by specific patient if provided
        if patient_id:
            patients_qs = patients_qs.filter(id=patient_id)

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        filename = f'patient_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'Patient ID', 'Patient Name', 'Patient Email', 'Patient Phone',
            'Date', 'Type', 'Details', 'Systolic', 'Diastolic', 'Heartrate',
            'Medication', 'Dosage', 'Frequency', 'Treatment', 'Status',
            'Appointment Date', 'Appointment Time', 'Reason'
        ])

        for patient in patients_qs:
            # Build filters for date range
            date_filter = {}
            if from_date:
                date_filter['created_at__gte'] = from_date
            if to_date:
                date_filter['created_at__lte'] = to_date + ' 23:59:59' if to_date else to_date

            patient_name = patient.user.get_full_name() or patient.user.username
            patient_email = patient.user.email
            patient_phone = patient.phone or ''

            # Export vitals
            vitals_qs = VitalReading.objects.filter(patient=patient.user)
            if date_filter:
                vitals_qs = vitals_qs.filter(**date_filter)
            
            for vital in vitals_qs.order_by('-created_at'):
                writer.writerow([
                    patient.id, patient_name, patient_email, patient_phone,
                    vital.created_at.strftime('%Y-%m-%d %H:%M'),
                    'Vital Reading',
                    f'Symptoms: {vital.symptoms or "None"}',
                    vital.systolic, vital.diastolic, vital.heartrate or '',
                    '', '', '', '', '', '', '', ''
                ])

            # Export prescriptions
            prescriptions_qs = Prescription.objects.filter(patient=patient)
            if date_filter:
                prescriptions_qs = prescriptions_qs.filter(**date_filter)
            
            for prescription in prescriptions_qs.order_by('-created_at'):
                writer.writerow([
                    patient.id, patient_name, patient_email, patient_phone,
                    prescription.created_at.strftime('%Y-%m-%d %H:%M'),
                    'Prescription',
                    prescription.instructions or '',
                    '', '', '',
                    prescription.medication, prescription.dosage, prescription.frequency,
                    '', '', '', '', ''
                ])

            # Export treatments
            treatments_qs = Treatment.objects.filter(patient=patient)
            if date_filter:
                treatments_qs = treatments_qs.filter(**date_filter)
            
            for treatment in treatments_qs.order_by('-created_at'):
                writer.writerow([
                    patient.id, patient_name, patient_email, patient_phone,
                    treatment.created_at.strftime('%Y-%m-%d %H:%M'),
                    'Treatment',
                    treatment.description,
                    '', '', '', '', '', '',
                    treatment.name, treatment.status,
                    '', '', ''
                ])

            # Export appointments
            appointments_qs = Appointment.objects.filter(patient=patient)
            if from_date or to_date:
                appt_date_filter = {}
                if from_date:
                    appt_date_filter['date__gte'] = from_date
                if to_date:
                    appt_date_filter['date__lte'] = to_date
                appointments_qs = appointments_qs.filter(**appt_date_filter)
            
            for appointment in appointments_qs.order_by('-date'):
                writer.writerow([
                    patient.id, patient_name, patient_email, patient_phone,
                    appointment.created_at.strftime('%Y-%m-%d %H:%M'),
                    'Appointment',
                    '',
                    '', '', '', '', '', '', '', '',
                    appointment.date.strftime('%Y-%m-%d') if appointment.date else '',
                    appointment.time.strftime('%H:%M') if appointment.time else '',
                    appointment.reason
                ])

        return response

def get_report_data_for_patient(patient, from_date=None, to_date=None):
    # Build filters for date range
    date_filter = {}
    if from_date:
        date_filter['created_at__gte'] = from_date
    if to_date:
        date_filter['created_at__lte'] = to_date + ' 23:59:59'

    # Get vitals
    vitals_qs = VitalReading.objects.filter(patient=patient.user)
    if date_filter:
        vitals_qs = vitals_qs.filter(**date_filter)
    vitals = vitals_qs.order_by('-created_at')

    # Get prescriptions
    prescriptions_qs = Prescription.objects.filter(patient=patient)
    if date_filter:
        prescriptions_qs = prescriptions_qs.filter(**date_filter)
    prescriptions = prescriptions_qs.order_by('-created_at')

    # Get treatments
    treatments_qs = Treatment.objects.filter(patient=patient)
    if date_filter:
        treatments_qs = treatments_qs.filter(**date_filter)
    treatments = treatments_qs.order_by('-created_at')

    # Get appointments
    appointments_qs = Appointment.objects.filter(patient=patient)
    if from_date or to_date:
        appt_date_filter = {}
        if from_date:
            appt_date_filter['date__gte'] = from_date
        if to_date:
            appt_date_filter['date__lte'] = to_date
        appointments_qs = appointments_qs.filter(**appt_date_filter)
    appointments = appointments_qs.order_by('-date')

    # Calculate statistics
    vitals_stats = vitals.aggregate(
        avg_systolic=Avg('systolic'),
        avg_diastolic=Avg('diastolic'),
        avg_heartrate=Avg('heartrate')
    )

    return {
        'patient_id': patient.id,
        'patient_name': patient.user.get_full_name() or patient.user.username,
        'patient_email': patient.user.email,
        'patient_phone': patient.phone or '',
        'total_vitals': vitals.count(),
        'total_prescriptions': prescriptions.count(),
        'total_treatments': treatments.count(),
        'total_appointments': appointments.count(),
        'avg_systolic': round(vitals_stats['avg_systolic'], 1) if vitals_stats['avg_systolic'] else None,
        'avg_diastolic': round(vitals_stats['avg_diastolic'], 1) if vitals_stats['avg_diastolic'] else None,
        'avg_heartrate': round(vitals_stats['avg_heartrate'], 1) if vitals_stats['avg_heartrate'] else None,
        'vitals': [
            {
                'id': v.id,
                'systolic': v.systolic,
                'diastolic': v.diastolic,
                'heartrate': v.heartrate,
                'symptoms': v.symptoms,
                'diet': v.diet,
                'exercise': v.exercise,
                'created_at': v.created_at.isoformat()
            }
            for v in vitals
        ],
        'prescriptions': [
            {
                'id': p.id,
                'medication': p.medication,
                'dosage': p.dosage,
                'frequency': p.frequency,
                'duration_days': p.duration_days,
                'instructions': p.instructions,
                'doctor_name': p.doctor.get_full_name() if hasattr(p.doctor, 'get_full_name') else 'N/A',
                'created_at': p.created_at.isoformat()
            }
            for p in prescriptions
        ],
        'treatments': [
            {
                'id': t.id,
                'name': t.name,
                'description': t.description,
                'status': t.status,
                'doctor_name': t.doctor.get_full_name() if hasattr(t.doctor, 'get_full_name') else 'N/A',
                'created_at': t.created_at.isoformat(),
                'updated_at': t.updated_at.isoformat()
            }
            for t in treatments
        ],
        'appointments': [
            {
                'id': a.id,
                'date': a.date.isoformat() if a.date else None,
                'time': a.time.isoformat() if a.time else None,
                'reason': a.reason,
                'status': a.status,
                'doctor_name': a.doctor.full_name if a.doctor else '',
                'created_at': a.created_at.isoformat()
            }
            for a in appointments
        ]
    }


class PatientReportPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, "profile"):
            return Response({"error": "Profile not found"}, status=404)
        
        patient = request.user.profile
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        report_data = get_report_data_for_patient(patient, from_date, to_date)
        pdf_buffer = ReportPDFService.generate_patient_report(report_data)
        
        filename = f"Report_{request.user.username}_{datetime.now().strftime('%Y%m%d')}.pdf"
        return FileResponse(pdf_buffer, as_attachment=True, filename=filename, content_type='application/pdf')


class DoctorPatientReportPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        if not hasattr(request.user, "doctor_profile"):
            return Response({"error": "Not authorized"}, status=403)
        
        patient = get_object_or_404(UserProfile, id=patient_id)
        # Ensure patient belongs to this doctor
        if patient.doctor != request.user.doctor_profile and not request.user.is_staff:
             return Response({"error": "You are not authorized to view this patient's report"}, status=403)

        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        report_data = get_report_data_for_patient(patient, from_date, to_date)
        pdf_buffer = ReportPDFService.generate_patient_report(report_data)
        
        filename = f"Report_{patient.user.username}_{datetime.now().strftime('%Y%m%d')}.pdf"
        return FileResponse(pdf_buffer, as_attachment=True, filename=filename, content_type='application/pdf')
