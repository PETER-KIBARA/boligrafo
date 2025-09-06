
from django.urls import path
from . import views

urlpatterns = [
path('apilogin', views.apilogin, name="apilogin"),
path("doctor/login", views.doctor_login, name="doctor_login"),
path("doctor/patients", views.doctor_patients),
path("doctor/profile", views.doctor_profile),
path("patient/signup", views.patient_signup, name="patient_signup"),

]