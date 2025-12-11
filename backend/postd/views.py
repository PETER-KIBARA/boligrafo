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
from .serializers import AppointmentSerializer
# from .models import Notification
#~from .serializers import NotificationSerializer



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

class NotificationDetailView(generics.RetrieveAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]



from django.contrib.auth import get_user_model
from django.http import HttpResponse

def create_admin(request):
    User = get_user_model()
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@example.com", "admin123")
        return HttpResponse("Superuser created ✅")
    else:
        return HttpResponse("Admin already exists.")



class AppointmentListCreateView(generics.ListCreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Doctor filters
        if hasattr(user, "doctor_profile"):
            patient_id = self.request.query_params.get("patient_id")
            if patient_id:
                return Appointment.objects.filter(patient_id=patient_id)

            return Appointment.objects.filter(doctor=user)

        # Patient filters
        return Appointment.objects.filter(patient__user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, "doctor_profile"):
            raise PermissionDenied("Only doctors can create appointments.")
        serializer.save(doctor=user)


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
