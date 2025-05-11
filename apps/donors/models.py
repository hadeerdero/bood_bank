from django.db import models
from users.models import User
from constants import BLOOD_TYPES
from apps.city.models import City
from apps.blood_stock.models import BloodStockProfile

class Donor(models.Model):
 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    national_id = models.CharField(max_length=14, unique=True)
    phone_number = models.CharField(max_length=15)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.national_id})"

   

class DonationRequest(models.Model):
    
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES, null=True, blank=True)
    donation_date = models.DateField(auto_now_add=True)
    last_donation_date = models.DateField(auto_now_add=True)
    virus_test_result = models.BooleanField(default=True)
    expiration_date = models.DateField(null=True)
    status = models.CharField(max_length=3, default='1')
    blood_stock = models.ForeignKey(BloodStockProfile, on_delete=models.CASCADE)
    note = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Donation request #{self.id} - {self.donor.name}"
    
    