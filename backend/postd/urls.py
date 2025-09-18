
from django.urls import path
from . import views
from .views import VitalReadingListCreateView
from .views import DoctorPatientDailyReportsView
from .views import PatientListView


urlpatterns = [
path('apilogin', views.apilogin, name="apilogin"),
path("doctor/login", views.doctor_login, name="doctor_login"),
path("doctor/patients", views.doctor_patients),
path("doctor/profile", views.doctor_profile),
path("list_patients", PatientListView.as_view(), name="patients-list"),
path("patient/signup", views.patient_signup, name="patient_signup"),
path("vitals", VitalReadingListCreateView.as_view(), name="vital-list-create"),
path('view_patient/<int:patient_id>/daily-reports', DoctorPatientDailyReportsView.as_view()),



]