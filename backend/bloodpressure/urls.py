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

def home(request):
    return HttpResponse("✅ Backend is running successfully on Render!")



urlpatterns = [
    path('api/', include('postd.urls')),
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

