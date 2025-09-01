from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from postd.models import UserProfile  
from postd.serializers import UserProfileSerializer
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

@api_view(['POST'])
@permission_classes([AllowAny])
def apisignup(request):
    """
    API endpoint for user signup (matches Flutter SignupScreen).
    """
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
    )

    serializer = UserProfileSerializer(profile)

    return Response({
        "message": "Account created successfully",
        "user": serializer.data
    }, status=201)
