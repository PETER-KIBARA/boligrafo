
from django.urls import path
from . import views

urlpatterns = [
    path('apisignup', views.apisignup, name='apisignup')
    
]