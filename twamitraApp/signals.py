from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CorporateAppointment

@receiver(post_save, sender=CorporateAppointment)
def update_is_completed(sender, instance, created, **kwargs):
    print("--------------------------------")
    print("Signal handler called")
    if instance.corporate_complete and instance.customer_complete:
        instance.is_completed = True
        print("Marking appointment as completed")
        instance.save()
