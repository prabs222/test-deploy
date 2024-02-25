from django.contrib import admin

# Register your models here.
from accountApp.models import User
@admin.register(User)
class account_detail(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_customer', 'is_corporate')