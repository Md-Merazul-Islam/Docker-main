from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=500, null=True, blank=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    otp_timestamp = models.DateTimeField(null=True, blank=True) 
    

    def __str__(self):
        return self.user.username
