"""
URL configuration for bloodpressure project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse
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


def home(request):
    return HttpResponse("✅ Backend is running successfully on Render!")



urlpatterns = [
    path('', include('postd.urls')),
    path('admin/', admin.site.urls),
    path('', home),
]


from django.contrib.auth import get_user_model

def reset_admin_password(request):
    User = get_user_model()
    try:
        user = User.objects.get(username="admin")
        user.set_password("admin123")
        user.save()
        return HttpResponse("✅ Password reset to 'admin123'")
    except User.DoesNotExist:
        return HttpResponse("❌ No user named 'admin' found")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("reset-admin-password/", reset_admin_password),  # temporary
]





  


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

# path("notifications", NotificationListView.as_view(), name="doctor-notifications"),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
