from rest_framework import serializers
from .models import UserProfile, VitalReading, Prescription, Treatment, Appointment
from django.db.models import Avg, Count


class ReportVitalSerializer(serializers.ModelSerializer):
    """Serializer for vital readings in reports"""
    class Meta:
        model = VitalReading
        fields = ['id', 'systolic', 'diastolic', 'heartrate', 'symptoms', 'diet', 'exercise', 'created_at']


class ReportPrescriptionSerializer(serializers.ModelSerializer):
    """Serializer for prescriptions in reports"""
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    
    class Meta:
        model = Prescription
        fields = ['id', 'medication', 'dosage', 'frequency', 'duration_days', 'instructions', 'doctor_name', 'created_at']


class ReportTreatmentSerializer(serializers.ModelSerializer):
    """Serializer for treatments in reports"""
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    
    class Meta:
        model = Treatment
        fields = ['id', 'name', 'description', 'status', 'doctor_name', 'created_at', 'updated_at']


class ReportAppointmentSerializer(serializers.ModelSerializer):
    """Serializer for appointments in reports"""
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'date', 'time', 'reason', 'status', 'doctor_name', 'created_at']


class PatientReportSerializer(serializers.Serializer):
    """Comprehensive patient report serializer"""
    patient_id = serializers.IntegerField()
    patient_name = serializers.CharField()
    patient_email = serializers.CharField()
    patient_phone = serializers.CharField()
    
    # Summary statistics
    total_vitals = serializers.IntegerField()
    total_prescriptions = serializers.IntegerField()
    total_treatments = serializers.IntegerField()
    total_appointments = serializers.IntegerField()
    
    avg_systolic = serializers.FloatField(allow_null=True)
    avg_diastolic = serializers.FloatField(allow_null=True)
    avg_heartrate = serializers.FloatField(allow_null=True)
    
    # Detailed data
    vitals = ReportVitalSerializer(many=True, read_only=True)
    prescriptions = ReportPrescriptionSerializer(many=True, read_only=True)
    treatments = ReportTreatmentSerializer(many=True, read_only=True)
    appointments = ReportAppointmentSerializer(many=True, read_only=True)


class ReportSummarySerializer(serializers.Serializer):
    """Summary statistics for the entire report"""
    total_patients = serializers.IntegerField()
    total_vitals = serializers.IntegerField()
    total_prescriptions = serializers.IntegerField()
    total_treatments = serializers.IntegerField()
    total_appointments = serializers.IntegerField()
    
    avg_systolic = serializers.FloatField(allow_null=True)
    avg_diastolic = serializers.FloatField(allow_null=True)
    avg_heartrate = serializers.FloatField(allow_null=True)
    
    date_from = serializers.DateField(allow_null=True)
    date_to = serializers.DateField(allow_null=True)
    
    patients = PatientReportSerializer(many=True, read_only=True)
