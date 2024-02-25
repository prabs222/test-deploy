from django.forms import ModelForm
from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django_recaptcha.fields import ReCaptchaField

class ProfileForm(ModelForm):
    class Meta:
        model = CorporateDB
        fields = ['companyName', 'experience', 'address', 'pan','alternatePhone', 'profilePic']
        
class FormWithCaptcha(forms.Form):
    captcha = ReCaptchaField()
