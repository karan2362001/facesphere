from django.urls import path
from . import views

urlpatterns = [
    
    path("",views.user_login,name='user_login'),
    path("home/",views.home,name='home'),
    path("employee/",views.Employee_view,name='Employee_view'),
    path("company/",views.Company_view,name='Company_view'),
]