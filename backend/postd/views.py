from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
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
from postd.serializers import DoctorProfileSerializer

@api_view(['POST'])
@login_required 
def apisignup(request):
    """
    API endpoint for user signup (matches Flutter SignupScreen).
    """
    if not hasattr(request.user, "doctor_profile"):
         return Response({"error": "Only doctors can register patients"}, status=403)

    data = request.data

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    phone = data.get("phone")
    address = data.get("address")
    dob = data.get("dob")   
    gender = data.get("gender")
    emergency_name = data.get("emergency_name")
    emergency_phone = data.get("emergency_phone")
    emergency_relation = data.get("emergency_relation")

    
    if not name or not email or not password or not confirm_password:
        return Response({"error": "Required fields missing"}, status=400)

    try:
        validate_email(email)
    except ValidationError:
        return Response({"error": "Invalid email format"}, status=400)

    if password != confirm_password:
        return Response({"error": "Passwords do not match"}, status=400)

    if User.objects.filter(username=email).exists():
        return Response({"error": "Email already registered"}, status=400)

    
    user = User.objects.create(
        username=email,
        email=email,
        first_name=name,
        password=make_password(password),
    )

    
    profile = UserProfile.objects.create(
        user=user,
        phone=phone,
        address=address,
        dob=dob,
        gender=gender,
        emergency_name=emergency_name,
        emergency_phone=emergency_phone,
        emergency_relation=emergency_relation,
        doctor=request.user.doctor_profile, 
    )

    serializer = UserProfileSerializer(profile)

    return Response({
        "message": "Account created successfully",
        "user": serializer.data
    }, status=201)

    
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

    return Response({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.first_name,
            "email": user.email,
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
        "specialty": doctor.specialty,
        "employee_id": doctor.employee_id,
        "title": doctor.title,
    }
    return Response(data, status=200)
