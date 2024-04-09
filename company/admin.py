from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.Company)
admin.site.register(models.Branch)