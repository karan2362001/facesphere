from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.hashers import make_password

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('1', 'Company'),
        ('2', 'Employee'),
      
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    
    def save(self, *args, **kwargs):
        if not self.pk or self.password:
            # If the user is being created (not updated),
            # set_password is used to hash the password.
            self.set_password(self.password)
        
        super().save(*args, **kwargs)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)