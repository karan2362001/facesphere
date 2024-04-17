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
     path("employee-report/",views.employee_report,name='employee_report'),
      path("report-employee/<int:employee_id>",views.report_employee,name='report_employee'),
     path('download-attendance-report1/<int:selected_year>/<int:selected_month>/<int:employee_id>', views.download_attendance_report1, name='download_attendance_report1'),
     path("salary-employee-form/<int:employee_id>",views.salary_employee_form,name='salary_employee_form'),
    path("salary-management/",views.salary_management,name='salary_management'),
    path("leave-deduction-rate/",views.leave_deduction_rate,name='leave_deduction_rate'),
    
  
     
]
