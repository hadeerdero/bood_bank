# # donations/signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.utils import timezone
# from datetime import timedelta
# from .models import DonationRequest
# from apps.blood_stock.models import BloodStock

# @receiver(post_save, sender=DonationRequest)
# def handle_donation_approval(sender, instance, created, **kwargs):
#     # Add debug prints
#     print(f"Signal triggered. Created: {created}, Approved: {instance.is_approved}, Existing: {hasattr(instance, 'blood_stock')}")
    
#     if instance.is_approved and not hasattr(instance, 'blood_stock'):
#         try:
#             blood_stock = BloodStock.objects.create(
#                 blood_type=instance.blood_type,
#                 quantity=1,
#                 city=instance.donor.city,
#                 expiration_date=timezone.now() + timedelta(days=42),
#                 donation=instance
#             )
#             instance.save()
#             print("BloodStock created successfully!")
#         except Exception as e:
#             print(f"Error creating BloodStock: {str(e)}")