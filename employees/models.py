from django.db import models

from company.models import Branch, Company
from accounts.models import CustomUser
# Create your models here.
class Employee(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    #branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='employees')
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    position = models.CharField(max_length=100)
    picture = models.ImageField(upload_to="employee\img", blank=True)
    face_encoding = models.JSONField(blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.user.username}_{self.company.name}"
    
    
    
    
class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('1', 'Present'), ('0', 'Absent')], default='0')
    
    def __str__(self):
        return f"{self.employee.username}_{self.company.name}_{self.branch.name}"
