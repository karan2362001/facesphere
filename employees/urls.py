from django.urls import path
from . import views

urlpatterns = [
    
    path("attendance-cam/",views.attendance_cam,name='attendance_cam'),
]