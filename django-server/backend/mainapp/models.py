from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class request_logs(models.Model):
    # string of format "%Y-%m-%d %H:%M:%S" eg. "2020-04-01 20:01:14", FORMAT = UTC
    timestamp=models.CharField(max_length=19, default='-')
    
    # emergency_type contains string one of 'health' & 'police'
    emergency_type=models.CharField(max_length=7, default='-')

    # core_id: id of sending device
    core_id = models.CharField(max_length=30, default='-')

    # latitude and longitude
    latitude = models.FloatField(default=-1.0)
    longitude = models.FloatField(default=-1.0)
    
    # pincode
    pincode = models.CharField(max_length=10, default="-")

    # accuracy
    accuracy = models.FloatField()

    # status: one of string: 'a' (active), 'w' (working), 'r' (resolved)
    status = models.CharField(max_length=1, default='a')

    def __str__(self):
        return self.timestamp + self.emergency_type + self.core_id

class UserProfile(models.Model):
    name = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    location = models.TextField(max_length=500, blank=True)         # user.profile.location
    service = models.CharField(max_length=8, blank=True)            # user.profile.service
    phone = models.CharField(max_length=13, blank=True)             # user.profile.phone

    def __str__(self) -> str:
        return self.name
