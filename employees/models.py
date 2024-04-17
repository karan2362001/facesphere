from django.db import models

from company_side.models import Branch, Company
from accounts.models import CustomUser
# Create your models here.
LEAVE_CHOICES = [
    ('sick_leave', 'Sick Leave'),
    ('vacation_leave', 'Vacation Leave'),
    ('casual_leave', 'Casual Leave'),
    ('earned_leave', 'Earned Leave'),
    ('maternity_leave', 'Maternity Leave'),
    ('paternity_leave', 'Paternity Leave'),
    ('bereavement_leave', 'Bereavement Leave'),
    ('compensatory_off', 'Compensatory Off'),
       ]

class Employee(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
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
    
    def delete(self, *args, **kwargs):
        # Delete the associated CustomUser instance
        self.user.delete()
        super().delete(*args, **kwargs)
    
    
    
    
class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(auto_now_add=True)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('1', 'Present'), ('0', 'Absent')], default='0')
    
    def __str__(self):
        return f"{self.employee.user.username}"


        
class Leave(models.Model):
    STATUS_CHOICES = [
        ('3', 'Pending'),
        ('1', 'Approved'),
        ('0', 'Rejected'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20,choices=STATUS_CHOICES, default='3')
    application_date=models.DateTimeField(auto_now_add=True, blank=True, null=True)
    leave_type = models.CharField(max_length=50, choices=LEAVE_CHOICES,blank=True, null=True)

    def __str__(self):
        return f"{self.employee.user.username}"
    
    
    
    
    


# Define choices for tax types for Indian employees
TAX_CHOICES_INDIA = [
    ('income_tax', 'Income Tax'),
    ('pf', 'Provident Fund (PF)'),
    ('esi', 'Employee State Insurance (ESI)'),
    ('professional_tax', 'Professional Tax'),
    ('tds', 'Tax Deducted at Source (TDS)'),
    # Add more tax types as needed
]

# Salary Information
class Salary_employee(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    housing_allowance = models.DecimalField(max_digits=10, decimal_places=2)
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2)
    # Add other allowances and deductions as needed
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)

    
    def __str__(self):
        return f"{self.employee.user.username}"
    



# Taxation and Compliance
class Tax(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    tax_type = models.CharField(max_length=50, choices=TAX_CHOICES_INDIA)  # Choice field for tax type for Indian employees
    amount = models.DecimalField(max_digits=10, decimal_places=2)

# Bank Details
    def __str__(self):
        return f"{self.employee.user.username}"

