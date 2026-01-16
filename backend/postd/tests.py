from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from postd.models import (
    UserProfile, DoctorProfile, VitalReading, Prescription, 
    Treatment, Appointment, AISuggestionConfig, AISuggestionLog
)
from postd.ai.services.suggestion_engine import SuggestionEngine

class AISuggestionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create Doctor
        self.doctor_user = User.objects.create_user(username='dr_house', password='password')
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user, 
            full_name="Gregory House",
            national_id="123",
            employee_id="456",
            specialty="Diagnostician",
            title="Dr."
        )
        
        # Create Patient
        self.patient_user = User.objects.create_user(username='patient_zero', password='password')
        self.patient_profile = UserProfile.objects.create(
            user=self.patient_user,
            phone="555-0100",
            gender="Male",
            dob="1980-01-01"
        )
        
        # Create Config
        self.config = AISuggestionConfig.objects.create(
            bp_systolic_threshold=140,
            bp_diastolic_threshold=90
        )
        
        self.url = reverse('generate_suggestions', kwargs={'patient_id': self.patient_user.id})

    def test_unauthenticated_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) # or 403 depending on default

    def test_non_clinician_access(self):
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_clinician_access_success(self):
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ai_suggestions', response.data)
        self.assertIn('patient_id', response.data)
        
        # Check audit log
        self.assertTrue(AISuggestionLog.objects.filter(patient=self.patient_profile, requested_by=self.doctor_user).exists())

    def test_patient_not_found(self):
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('generate_suggestions', kwargs={'patient_id': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_high_bp_suggestion_generation(self):
        # Setup data for High BP Rule (R002)
        # Add Prescriptions (Active)
        p = Prescription.objects.create(
            doctor=self.doctor_user,
            patient=self.patient_profile,
            medication="Lisinopril",
            dosage="10mg",
            frequency="Daily",
            duration_days=90,
            created_at=timezone.now() - timedelta(days=60)
        )
        
        # Add Vitals (High BP recently)
        VitalReading.objects.create(
            patient=self.patient_user,
            systolic=150,
            diastolic=95,
            heartrate=80,
            created_at=timezone.now()
        )
        
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        suggestions = response.data['ai_suggestions']
        
        # We expect at least one suggestion related to High BP or Compliance
        # Ideally check rule_id if possible
        rule_ids = [s.get('rule_id') for s in suggestions]
        # Depending on engine logic R002 should trigger if High BP + Active Meds
        self.assertTrue(any(rid in ['R001', 'R002'] for rid in rule_ids), f"Expected R001 or R002, got {rule_ids}")

    def test_improving_trend_suggestion(self):
        # Setup improving vitals
        # Oldest: High
        VitalReading.objects.create(
            patient=self.patient_user,
            systolic=160,
            diastolic=100,
            created_at=timezone.now() - timedelta(days=30)
        )
        # Middle: Lower
        VitalReading.objects.create(
            patient=self.patient_user,
            systolic=140,
            diastolic=90,
            created_at=timezone.now() - timedelta(days=15)
        )
        # Newest: Good
        VitalReading.objects.create(
            patient=self.patient_user,
            systolic=120,
            diastolic=80,
            created_at=timezone.now()
        )
        
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.get(self.url)
        suggestions = response.data['ai_suggestions']
        rule_ids = [s.get('rule_id') for s in suggestions]
        # Expect R004 (Improving trend)
        self.assertIn('R004', rule_ids)
