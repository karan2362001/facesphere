from django.urls import path
from . import views

urlpatterns = [
    
    path("add-employee/",views.add_employee,name='add_employee'),
    path("manage-employee/",views.manage_employee,name='manage_employee'),
    path("set-geofencing/",views.set_geofencing,name='set_geofencing'),
     path("view_analytics/",views.view_analytics,name='view_analytics'),
     path("show-details-employee/<int:employee_id>",views.show_details_employee,name='show_details_employee'),
     path("edit-details-employee/<int:employee_id>",views.edit_details_employee,name='edit_details_employee'),
     path("delete-details-employee/<int:employee_id>",views.delete_details_employee,name='delete_details_employee'),
     path("manage-employee-leave/",views.manage_employee_leave,name='manage_employee_leave'),
     path("manage-employee-leave-approve/<int:leave_id>",views.manage_employee_leave_approve,name='manage_employee_leave_approve'),
     path("manage-employee-leave-reject/<int:leave_id>",views.manage_employee_leave_reject,name='manage_employee_leave_reject'),
     
]
