from django.contrib import admin
from .models import UserProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import VitalReading
from .models import DoctorProfile
from .models import Prescription

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "gender", "dob")
    search_fields = ("user__username", "phone", "gender")

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "specialty", "employee_id", "national_id", "title")

class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    verbose_name_plural = "Doctor Profile"
    fk_name = "user"

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



class VitalReadingInline(admin.TabularInline):
    model = VitalReading   # <-- Fix here
    extra = 0
    readonly_fields = ("systolic", "diastolic", "symptoms", "created_at")
    can_delete = False
    verbose_name_plural = "Vital Readings"
    fk_name = "patient" 

# Unregister the default User admin
admin.site.unregister(User)
# Register User with our custom admin
admin.site.register(User, UserAdmin)

admin.site.register(VitalReading)