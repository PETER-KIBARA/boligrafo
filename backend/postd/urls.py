
from django.urls import path
from . import views

urlpatterns = [
    path('apisingup', views.apisignup, name='apisignup')
    
]