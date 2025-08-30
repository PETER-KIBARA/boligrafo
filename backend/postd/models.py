from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, username, phone, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field is required")
        if not phone:
            raise ValueError("The Phone number is required")
        
        user = self.model(username=username, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, phone, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Login identifiers
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True)

    # Profile details
    address = models.TextField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)

    # Emergency contact
    emergency_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_relation = models.CharField(max_length=50, blank=True, null=True)

    # Permissions
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"   # you could switch to "phone" if preferred
    REQUIRED_FIELDS = ["phone"]

    def __str__(self):
        return self.username
