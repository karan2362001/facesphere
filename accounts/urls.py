from django.urls import path
from . import views

urlpatterns = [
    
    path("",views.user_login,name='user_login'),
    path("home/",views.home,name='home'),
    path("employee/",views.Employee,name='Employee'),
    path("company/",views.Company,name='Company'),
]