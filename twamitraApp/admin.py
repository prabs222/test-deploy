from django.contrib import admin
from twamitraApp.models import *

# Register your models here.
@admin.register(LoanDetail)
class load_details(admin.ModelAdmin):
    list_display = ('name', 'email', 'loan_type', 'loan_amount')  # Customize the fields displayed in the admin list view

admin.site.register(GeneratedCode)
admin.site.register(Professions)

class CorporateAdmin(admin.ModelAdmin):
    list_display = ('user','profession', 'location', 'is_active')
admin.site.register(CorporateDB, CorporateAdmin)

admin.site.register(CorporatePayments)
admin.site.register(ServiceType)
admin.site.register(SubscriptionType)
admin.site.register(AppointmentPayment)
admin.site.register(CorporateAppointment)
admin.site.register(LoanType)
admin.site.register(UserDB)


