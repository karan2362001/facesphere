from django.urls import path
from . import views

urlpatterns = [
    
    path("add-employee/",views.add_employee,name='add_employee'),
    path("manage-employee/",views.manage_employee,name='manage_employee'),
    path("set-geofencing/",views.set_geofencing,name='set_geofencing'),
     path("view_analytics/",views.view_analytics,name='view_analytics'),
     path("show-details-employee/",views.show_details_employee,name='show_details_employee'),
]