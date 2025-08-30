from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "phone", "email", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "gender")
    search_fields = ("username", "phone", "email")
    ordering = ("username",)

admin.site.register(CustomUser, CustomUserAdmin)
