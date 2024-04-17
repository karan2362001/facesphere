from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.Company)
admin.site.register(models.Branch)
admin.site.register(models.Company_geo_f_set)
admin.site.register(models.LeaveDeductionRate)