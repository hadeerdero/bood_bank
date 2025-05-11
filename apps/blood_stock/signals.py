# blood_stock/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from apps.Hospitals.models import BloodRequest

@receiver(post_save, sender=BloodRequest)
def notify_request_status(sender, instance, **kwargs):
    if instance.status == 'rejected':
        send_mail(
            f"Blood Request {instance.id} Rejected",
            f"Your request for {instance.blood_type} blood could not be fulfilled.",
            'bloodbank@system.com',
            [instance.hospital.user.email],
            fail_silently=False
        )