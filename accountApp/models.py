from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    name =  models.CharField(max_length=200,null=True, blank=True)
    email = models.EmailField(unique=True, null=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(max_length=15, validators=[phone_regex], null=True)
    is_customer = models.BooleanField(default=False)
    is_corporate = models.BooleanField(default=False)
        
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email


# class CorporateDB(AbstractUser):
#     cid = models.CharField(max_length=7, primary_key=True, unique=True)
#     name = models.CharField(max_length=255)
#     businessName = models.CharField(max_length=255)
#     profession = models.ForeignKey(Professions,on_delete=models.CASCADE)
#     email = models.EmailField(unique=True, null=True)
#     phone = models.CharField(max_length=15)
#     location = models.CharField(max_length=255)
#     referralCode = models.CharField(max_length=8,null=True)
#     razorpay_order_id = models.CharField(max_length=255,null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     has_paid = models.BooleanField(default=False)
#     subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.SET_NULL,null=True)
#     active_till = models.DateField(auto_now_add=False)
#     is_active = models.BooleanField(default=False)
#     is_corporate = models.BooleanField(default=True)
        
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []

#     def __str__(self) -> str:
#         return self.name
