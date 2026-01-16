from typing import Dict, Any
from django.http import JsonResponse, Http404
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from .services.suggestion_engine import SuggestionEngine
from postd.models import UserProfile, AISuggestionConfig, AISuggestionLog, DoctorProfile
from .serializers import PatientProfileSerializer

class GenerateSuggestionsView(APIView):
    """
    GET /api/generate_suggestions/<patient_id>/
    Triggered explicitly by the clinician.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id, *args, **kwargs):
        # 1. Permission Check: Only doctors/clinicians
        if not hasattr(request.user, 'doctor_profile'):
             return Response({"detail": "Only clinicians can access AI suggestions."}, status=status.HTTP_403_FORBIDDEN)

        # 2. Get Patient
        # patient_id here is likely the User ID based on original code usage "patient_id != 1", 
        # but models say UserProfile links to User. 
        # Let's assume the URL passes the User ID of the patient (common pattern). 
        # If it passes UserProfile ID, we'd adjust.
        # Looking at urls.py: path('generate_suggestions/<int:patient_id>/', ...)
        # Current logic in views.py used int(patient_id).
        # We will assume patient_id is the ID of the User model who is a patient. 
        # Actually UserProfile has a patient_id property which is user.id. 
        # Let's try to get UserProfile by user_id first.
        
        try:
             profile = UserProfile.objects.get(user__id=patient_id)
        except UserProfile.DoesNotExist:
             return Response({"detail": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

        # 3. Assemble Profile Data
        serializer = PatientProfileSerializer(profile)
        patient_data = serializer.data

        # 4. Load Configuration
        config_obj = AISuggestionConfig.get_solitary()
        config = {
            "bp_systolic_threshold": config_obj.bp_systolic_threshold,
            "bp_diastolic_threshold": config_obj.bp_diastolic_threshold,
            "trend_slope_threshold": config_obj.trend_slope_threshold,
            "adherence_threshold": config_obj.adherence_threshold
        }

        # 5. Run Engine
        engine = SuggestionEngine(config=config)
        suggestions = engine.evaluate(patient_data)

        # 6. Audit Logging
        AISuggestionLog.objects.create(
            requested_by=request.user,
            patient=profile,
            suggestions_generated=suggestions
        )

        response = {
            "patient_id": patient_data["patient_id"],
            "ai_suggestions": suggestions,
            "config_used": config # Optional for debugging/transparency
        }
        return Response(response, status=status.HTTP_200_OK)