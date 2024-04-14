from django.urls import path
from . import views

urlpatterns = [
    
    path("attendance-cam/",views.attendance_cam,name='attendance_cam'),
    path("leave-management/",views.leave_management,name='leave_management'),
    path("apply-leave/",views.apply_leave,name='apply_leave'),
    path("employee-attendance-report/",views.employee_attendance_report,name='employee_attendance_report')
]