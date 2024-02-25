from django.db import models
from accountApp.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class SubscriptionType(models.Model):
    type = models.CharField(max_length=20)
    value = models.PositiveIntegerField()
    default_price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.type
    
class Professions(models.Model):
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
        
    def __str__(self) -> str:
        return self.name

def corporate_profile_pic_path(instance, filename):
    return f'Images/corporates/profile/user_{instance.cid}-{filename}'

def user_signature_path(instance, filename):
    return f'Images/corporates/signature/user_{instance.cid}-{filename}'

def user_profile_pic_path(instance, filename):
    return f'Images/customer/profile/user_{instance.user.id}-{filename}'


class UserDB(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    address = models.TextField(null=True)
    pincode = models.CharField(max_length=10,null=True)
    pan = models.CharField(max_length=20,null=True)
    profilePic = models.ImageField(upload_to=user_profile_pic_path,default='userDefault.svg',null=True)
    is_active = models.BooleanField(default=True)
    
    updated_at = models.DateTimeField(auto_now = True)
    
    def __str__(self):
        return self.user.email



class CorporateDB(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cid = models.CharField(max_length=7, unique=True)
    businessName = models.CharField(max_length=255)
    profession = models.ForeignKey(Professions,on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    companyName = models.CharField(max_length=255,null=True)
    experience = models.CharField(max_length=255,null=True)
    address = models.TextField(null=True)
    pincode = models.CharField(max_length=10,null=True)
    pan = models.CharField(max_length=20,null=True)
    aadhar = models.CharField(max_length=15,null=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    alternatePhone = models.CharField(max_length=15, validators=[phone_regex], null=True)
    profilePic = models.ImageField(upload_to=corporate_profile_pic_path,null=True,default='userDefault.svg')
    has_paid = models.BooleanField(default=False)
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.SET_NULL,null=True)
    active_till = models.DateField(auto_now_add=False,null=True)
    is_active = models.BooleanField(default=False)
    terms_accepted = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    total_ratings = models.IntegerField(default=0)
    
    def __str__(self) -> str:
        return self.user.name

class CorporatePayments(models.Model):
    cid = models.ForeignKey(CorporateDB,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.SET_NULL,null=True)
    referralUsed = models.BooleanField(default=False)
    referralCode = models.CharField(max_length=8,null=True)
    razorpay_order_id = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255,null=True)
    razorpay_signature = models.CharField(max_length=255,null=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f'{self.cid.user.name} - {self.subscription_type} - {self.amount}'
    
class LoanType(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self) -> str:
        return self.name


class LoanDetail(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans', null=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(max_length=15, validators=[phone_regex])
    loan_type = models.ForeignKey(LoanType, on_delete=models.CASCADE)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2)
    year_salary=models.DecimalField(max_digits=10, decimal_places=2)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_verified = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class GeneratedCode(models.Model):
    code = models.CharField(max_length=8, unique=True, null=False)
    PERCENTAGE_CHOICES = [
        ('25', '25'),
        ('50', '50'),
        ('75', '75'),
        ('100', '100'),
    ]
    percentage = models.CharField(max_length=20, choices=PERCENTAGE_CHOICES,null=False,default='25%')
    is_redeemed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_datetime = models.DateTimeField()  # Add this field
    is_expired = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Set expiration_datetime to 48 hours from now when creating or updating the code
        if not self.expiration_datetime:
            self.expiration_datetime = timezone.now() + timedelta(hours=48)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code

class ServiceType(models.Model):
    name = models.CharField(max_length=150)
    alias = models.CharField(max_length=150)
    profession = models.ForeignKey(Professions,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
   
    def __str__(self) -> str:
        return f'{self.name} - {self.profession.name}'
    
class CorporateAppointment(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    serviceType = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    corporate = models.ForeignKey(CorporateDB, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_confirmed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    corporate_complete = models.BooleanField(default=False)
    customer_complete = models.BooleanField(default=False)
    review = models.TextField(blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=255)
    

    def __str__(self):
        return f"{self.customer.email} - {self.serviceType.name} - {self.corporate.businessName}"

    class Meta:
        ordering = ['created_at', 'updated_at']
        
class AppointmentPayment(models.Model):
    appointment = models.ForeignKey(CorporateAppointment,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255,null=True)
    razorpay_signature = models.CharField(max_length=255,null=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f'{self.appointment.customer.email} - {self.appointment.serviceType.name}'
