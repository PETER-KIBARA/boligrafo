from rest_framework import serializers
from postd.models import VitalReading, Prescription, Treatment, Appointment, UserProfile
from django.utils import timezone
from datetime import datetime

class VitalReadingSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(source='created_at', format="%Y-%m-%dT%H:%M:%S")
    heart_rate = serializers.IntegerField(source='heartrate', required=False, allow_null=True)

    class Meta:
        model = VitalReading
        fields = ['timestamp', 'systolic', 'diastolic', 'heart_rate']


class PrescriptionSerializer(serializers.ModelSerializer):
    started_at = serializers.DateTimeField(source='created_at', format="%Y-%m-%dT%H:%M:%S")
    active = serializers.SerializerMethodField()
    ended_at = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = ['medication', 'started_at', 'ended_at', 'active', 'duration_days', 'dosage', 'frequency']

    def get_active(self, obj):
        # Infer active status: if created_at + duration_days > now
        if not obj.created_at:
            return False
        end_date = obj.created_at + timezone.timedelta(days=obj.duration_days)
        return timezone.now() <= end_date

    def get_ended_at(self, obj):
        if not obj.created_at:
            return None
        end_date = obj.created_at + timezone.timedelta(days=obj.duration_days)
        return end_date.strftime("%Y-%m-%dT%H:%M:%S")


class TreatmentSerializer(serializers.ModelSerializer):
    treatment = serializers.CharField(source='name')
    started_at = serializers.DateTimeField(source='created_at', format="%Y-%m-%dT%H:%M:%S")
    ended_at = serializers.DateTimeField(source='updated_at', format="%Y-%m-%dT%H:%M:%S", allow_null=True) # Using updated_at as proxy for ended if completed
    outcome = serializers.SerializerMethodField()

    class Meta:
        model = Treatment
        fields = ['treatment', 'started_at', 'ended_at', 'outcome']

    def get_outcome(self, obj):
        # Logic to map status/description to outcome
        # For now, we return None as the model doesn't explicitly store clinical outcome
        # Could key off keywords in description if needed.
        return None 


class AppointmentSerializer(serializers.ModelSerializer):
    scheduled_at = serializers.SerializerMethodField()
    attended = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['scheduled_at', 'attended', 'status']

    def get_scheduled_at(self, obj):
        if obj.date and obj.time:
            dt = datetime.combine(obj.date, obj.time)
            return dt.isoformat()
        return None

    def get_attended(self, obj):
        if obj.status == 'completed':
            return True
        if obj.status == 'missed':
            return False
        return None


class PatientProfileSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField(source='user.id') # Maps to User ID as per UserProfile logic
    vitals = serializers.SerializerMethodField()
    prescriptions = serializers.SerializerMethodField()
    treatments = serializers.SerializerMethodField()
    appointments = serializers.SerializerMethodField()
    as_of = serializers.SerializerMethodField()

    def get_vitals(self, obj):
        # Fetch vitals for this patient, oldest -> newest
        vlm = obj.user.vitals.all().order_by('created_at')
        return VitalReadingSerializer(vlm, many=True).data

    def get_prescriptions(self, obj):
        # Fetch prescriptions; Prescription model links to UserProfile via 'patient'
        # BUT Prescription definition: patient = ForeignKey("UserProfile", ...)
        # So obj.prescriptions.all() works
        pm = obj.prescriptions.all().order_by('-created_at')
        return PrescriptionSerializer(pm, many=True).data

    def get_treatments(self, obj):
        # Treatment: patient = ForeignKey("UserProfile", ...)
        tm = obj.treatments.all().order_by('-created_at')
        return TreatmentSerializer(tm, many=True).data

    def get_appointments(self, obj):
        # Appointment: patient = ForeignKey("postd.UserProfile", ...)
        am = obj.appointments.all().order_by('date', 'time')
        return AppointmentSerializer(am, many=True).data

    def get_as_of(self, obj):
        return timezone.now().strftime("%Y-%m-%dT%H:%M:%S")
