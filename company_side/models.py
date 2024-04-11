from django.db import models

# Create your models here.
from accounts.models import CustomUser

class Company(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    phone_number = models.CharField(max_length=20)
    logo = models.ImageField(upload_to="logo/", blank=True, null=True)
    location_range= models.IntegerField()

    
    def __str__(self):
        return self.name
    
    
class Branch(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_range= models.IntegerField()
    
    def __str__(self):
        return f"{self.name}_{self.company.name}"