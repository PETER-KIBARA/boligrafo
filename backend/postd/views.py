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
from .serializers import TreatmentSerializer
# from .models import Notification
# from .serializers import NotificationSerializer



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
    Return logged-in doctor's profile info
    """
    if not hasattr(request.user, "doctor_profile"):
        return Response({"error": "Not authorized"}, status=403)

    doctor = request.user.doctor_profile
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
    }
    return Response(data, status=200)




class VitalReadingListCreateView(generics.ListCreateAPIView):
    serializer_class = VitalReadingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VitalReading.objects.filter(patient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)



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
        qs = Prescription.objects.all()

        if hasattr(user, "doctor_profile"):
            patient_id = self.request.query_params.get("patient")
            if patient_id:
                qs = qs.filter(patient_id=patient_id)
            return qs

        if hasattr(user, "userprofile"):
            return qs.filter(patient=user.userprofile)

        return Prescription.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, "doctor_profile"):
            raise PermissionDenied("Only doctors can create prescriptions.")
        serializer.save(doctor=user)  # FIXED LINE
        
class PrescriptionRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user
        if not hasattr(user, "doctor_profile"):
            raise PermissionDenied("Only doctors can update prescriptions.")
        serializer.save(doctor=user)  # FIXED LINE



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




# class NotificationListView(generics.ListAPIView):
#     serializer_class = NotificationSerializer   # 💡 FIX
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         return Notification.objects.filter(doctor=user).order_by("-created_at")
