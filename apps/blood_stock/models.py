from django.db import models
from constants import BLOOD_TYPES, BLOOD_STORAGE_TYPES
from apps.city.models import City
from users.models import User
# Create your models here.

class BloodStockProfile(models.Model):
 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"


# class BloodStock(models.Model):
#     blood_stock = models.ForeignKey(BloodStockProfile, on_delete=models.CASCADE)
#     blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)
#     quantity = models.PositiveIntegerField(default=1)
#     city = models.ForeignKey(City, on_delete=models.CASCADE)
#     expiration_date = models.DateField()
#     donation = models.ForeignKey(
#         DonationRequest,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='blood_units'
#     )

#     def __str__(self):
#         return f"{self.blood_type} in {self.city} (Exp: {self.expiration_date})"
    