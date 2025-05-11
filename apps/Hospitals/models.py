from django.db import models
from users.models import User
from constants import BLOOD_TYPES, URGENCY
from apps.city.models import City

class HospitalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

class BloodRequest(models.Model):
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)
    urgency = models.CharField(max_length=10, choices=URGENCY)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=50, default='1')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-urgency']  # Sort by urgency first, then location

    def __str__(self):
        return f"Request #{self.id} - {self.blood_type} ({self.urgency})"
