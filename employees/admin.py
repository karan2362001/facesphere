from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.Employee)
admin.site.register(models.Attendance)
admin.site.register(models.Leave)
admin.site.register(models.Salary_employee)
admin.site.register(models.Tax)