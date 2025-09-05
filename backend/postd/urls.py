
from django.urls import path
from . import views

urlpatterns = [
    path('apisignup', views.apisignup, name='apisignup'),
path('apilogin', views.apilogin, name="apilogin"),
    path("doctor/login", views.doctor_login, name="doctor_login"),

]