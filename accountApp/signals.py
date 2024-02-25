from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up

@receiver(user_signed_up)
def on_social_signup(sender, request, user, **kwargs):
    user.is_customer = True
    user.save()
