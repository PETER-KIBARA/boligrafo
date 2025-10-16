
from django.urls import path
from . import views
from .views import VitalReadingListCreateView
from .views import DoctorPatientDailyReportsView
from .views import PatientListView
from .views import PrescriptionListCreateView, PrescriptionRetrieveUpdateView
from .views import TreatmentListCreateView, TreatmentDetailView, DoctorVitalReadingListView
from django.conf import settings
from django.conf.urls.static import static
from .views import DoctorAllPatientsVitalsView
from .views import create_admin
from .views import NotificationListView
from .views import UserProfileListView
from .views import NotificationDetailView  



  


urlpatterns = [
path('apilogin', views.apilogin, name="apilogin"),
path("doctor/login", views.doctor_login, name="doctor_login"),
path("doctor/patients", views.doctor_patients),
path("doctor/profile", views.doctor_profile),
path("list_patients", PatientListView.as_view(), name="patients-list"),
path("patient/signup", views.patient_signup, name="patient_signup"),
path("vitals", VitalReadingListCreateView.as_view(), name="vital-list-create"),
path('view_patient/<int:patient_id>/daily-reports', DoctorPatientDailyReportsView.as_view()),
path("doctor/logout", views.logout_view, name="doctor-logout"),
path("prescriptions", PrescriptionListCreateView.as_view(), name="prescription-list-create"),
path("prescriptions/<int:pk>", PrescriptionRetrieveUpdateView.as_view(), name="prescription-detail"),
path("doctor/treatments", TreatmentListCreateView.as_view(), name="treatment-list"),
path("doctor/treatments/<int:pk>", TreatmentDetailView.as_view(), name="treatment-detail"),
path('doctor/vitals', views.DoctorVitalReadingListView.as_view(), name='doctor-vitals'),
path('doctor/all-vitals', views.DoctorAllPatientsVitalsView.as_view(), name='doctor-all-vitals'),
path("userprofiles", UserProfileListView.as_view(), name="userprofile-list"),
path('create-admin/', create_admin),
path('notifications/', NotificationListView.as_view(), name='notifications'),
path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),




]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
