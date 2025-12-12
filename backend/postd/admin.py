from django.contrib import admin
from .models import UserProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import VitalReading
from .models import DoctorProfile
from .models import Prescription
from .models import Treatment
from .models import Notification
from .models import PrescriptionLog




@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "gender", "dob")
    search_fields = ("user__username", "phone", "gender")

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "specialty", "employee_id", "national_id", "title", "profile_picture")

class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    verbose_name_plural = "Doctor Profile"
    fk_name = "user"


@admin.register(PrescriptionLog)
class PrescriptionLogAdmin(admin.ModelAdmin):
    list_display = ('patient', 'prescription', 'taken_at')
    list_filter = ('taken_at', 'patient')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'prescription__medication')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        "doctor",
        "patient",
        "medication",
        "dosage",
        "frequency",
        "duration_days",
        "created_at",
    )
    list_filter = ("doctor", "patient", "created_at")
    search_fields = (
        "medication",
        "dosage",
        "frequency",
        "patient__user__username",
        "doctor__username",
    )
    readonly_fields = ("created_at",)

class UserAdmin(BaseUserAdmin):
    inlines = (DoctorProfileInline,)
    list_display = ("username", "email", "first_name", "last_name", "is_staff")



@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "patient",
        "doctor",
        "status",       
        "created_at",
        "updated_at",
    )
    list_filter = ("doctor", "patient", "status", "created_at")
    search_fields = (
        "name",
        "description",
        "patient__user__first_name",
        "patient__user__last_name",
        "doctor__first_name",
        "doctor__last_name",
    )
    ordering = ("-created_at",)
    list_editable = ("status",) 
    date_hierarchy = "created_at"


@admin.register(VitalReading)
class VitalReadingAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'patient_column',
        'bp_column', 
        'hr_column',
        'created_date',
        'created_time'
    ]
    
    list_filter = ['created_at', 'patient']
    search_fields = ['patient__first_name', 'patient__last_name']
    list_per_page = 30
    
    def patient_column(self, obj):
        name = f"{obj.patient.first_name} {obj.patient.last_name}".strip()
        return name or obj.patient.username
    patient_column.short_description = 'Patient'
    patient_column.admin_order_field = 'patient__first_name'
    
    def bp_column(self, obj):
        return f"{obj.systolic}/{obj.diastolic}"
    bp_column.short_description = 'BP'
    
    def hr_column(self, obj):
        return obj.heartrate or "-"
    hr_column.short_description = 'HR'
    
    def created_date(self, obj):
        return obj.created_at.date()
    created_date.short_description = 'Date'
    created_date.admin_order_field = 'created_at'
    
    def created_time(self, obj):
        return obj.created_at.time()
    created_time.short_description = 'Time' 
    
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'doctor', 'patient', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'doctor__user__username', 'patient__user__username')
    ordering = ('-created_at',)





# Unregister the default User admin
admin.site.unregister(User)
# Register User with our custom admin
admin.site.register(User, UserAdmin)
