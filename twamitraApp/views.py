import random
import re
from django.shortcuts import render, redirect
from decimal import Decimal

from chatApp.models import ChatMessage, Thread
from .models import *
from .forms import FormWithCaptcha, ProfileForm
import uuid
from datetime import datetime, timedelta
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.contrib.auth import logout, authenticate , login
from django.db import transaction
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import is_corporate_user, is_customer
from django.db.models import Max, Count, Avg


razorpay_client = razorpay.Client(
        auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

def index(request):
    return render(request, "home.html")

def about(request):
    return render(request, "about.html")

def is_valid_email(email):
    allowed_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com', 'aol.com', 'protonmail.com', 'zoho.com', 'mail.com', 'yandex.com', 'gmx.com', 'live.com', 'inbox.com', 'fastmail.com', 'tutanota.com', 'rocketmail.com', 'rediffmail.com', 'lycos.com', 'mail.ru', 'cox.net', 'verizon.net', 'att.net', 'sbcglobal.net', 'earthlink.net', 'charter.net', 'optonline.net', 'mailinator.com', 'gmx.us', 'juno.com', 'netzero.net', 'hushmail.com', 'runbox.com', 'disroot.org', 'riseup.net', 'tormail.org', 'keemail.me']
    domain = email.split('@')[-1]
    if domain in allowed_domains:
        return True
    else:
        return False

def corporateRegistration(request):
    form = FormWithCaptcha()
    context = {"professions": Professions.objects.all(), "form": form}
    if request.method == 'POST':
        name = request.POST.get('name')
        businessName = request.POST.get('businessName')
        profession_name = request.POST.get('profession')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        location = request.POST.get('location')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        accept_terms = request.POST.get('accept_terms')
        form = FormWithCaptcha(request.POST)
        if(form.is_valid()):
            if not accept_terms:
                messages.error(request, {'status': 'error', 'message': 'You must agree to the Terms and Conditions.'})
                return render(request, "corporateRegistration.html", context)

            if(not name or not email or not phone or not businessName or not profession_name or not location or not password1 or not password2):
                messages.error(request, {'status': 'error', 'message': 'Enter all required fields'})
                return render( request, "corporateRegistration.html")
                            
            if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", password1):
                messages.error(request, {'status': 'error', 'message': 'Password validations failed. Please make sure your password is at least 8 characters long and contains at least one digit, one special character, and one uppercase letter.'})
                return render(request, "corporateRegistration.html", context)
            
            if not re.match(r"^[6-9]\d{9}$", phone):
                messages.error(request, {'status': 'error', 'message': 'Please enter a valid 10-digit phone number!'})
                return render(request, "corporateRegistration.html", context)

            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                messages.error(request, {'status': 'error', 'message': 'Invalid email format. Please enter a valid email address.'})
                return render(request, "corporateRegistration.html", context)

            if not is_valid_email(email):
                messages.error(request, {'status': 'error', 'message': 'Invalid email domain. Please use an email from a valid email service provider.'})
                return render(request, "corporateRegistration.html", context)


            if(password1 != password2):
                messages.error(request, {'status': 'error', 'message': 'Oops! Password mismatch!'})
                return render( request, "corporateRegistration.html")                
            profession = Professions.objects.get(name=profession_name)
            profession_mapping = {
                    'CA': 'C',
                    'ARCHITECT/VALUER': 'E',
                    'ADVOCATE/LEGAL ADVISOR': 'L',
                    'DSA': 'D',
                    'OTHERS': 'O',
                }
            profession_code = profession_mapping.get(profession.name, 'O')
            random_number = str(random.randint(1, 9999)).zfill(4)
            generated_id = f'C{random_number}{profession_code}{name[0]}'
            while CorporateDB.objects.filter(cid=generated_id).exists():
                random_number = str(random.randint(1, 9999)).zfill(4)
                generated_id = f'C{random_number}{profession_code}{name[0]}'
            try:
                with transaction.atomic():
                    user = User.objects.create_user(username=email, name=name, phone=phone, email=email,password=password1,is_corporate=True)
                    corporate = CorporateDB.objects.create(                
                        user=user,
                        cid=generated_id,
                        businessName=businessName,
                        profession=profession,
                        location=location,
                        is_active=False,
                        terms_accepted = True
                    )
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            except Exception as e:
                print(e)
                messages.error(request, {'status': 'error', 'message': 'Username already Taken! Try With another Username...'})
                return render( request, "corporateRegistration.html", context)
            return redirect ('corporateDashboard')
        else:
            messages.error(request, {'status': 'error', 'message': 'reCAPTCHA validation failed.'})
            return render(request, "corporateRegistration.html",context)
    else:
        return render(request, "corporateRegistration.html",context)

# @user_passes_test(is_corporate_user)
@login_required(login_url='/corporateLogin/')
def corporateDashboard(request):
    if not is_corporate_user(request.user):
        messages.error(request, {'status': 'error', 'message': 'Access forbidden for non-corporate users.'})
        return redirect('userDashboard','service')

    user = User.objects.get(email=request.user.email)
    corporate = CorporateDB.objects.get(user=request.user)
    services = ServiceType.objects.filter(profession=corporate.profession,corporateappointment__corporate=corporate).annotate(count=Count('corporateappointment'))
    threads = Thread.objects.by_user(user=user).prefetch_related('messages').order_by('-created_at')
    last_messages = []

    for thread in threads:
        last_message = thread.messages.aggregate(Max('timestamp'))['timestamp__max']
        last_messages.append({'thread_id': thread.id, 'last_message': last_message})

    print(services)
    context = {'user': user, 'corporate': corporate,'services': services, 'threads': threads, 'last_messages': last_messages}
    return render(request, "corporateDashboard.html", context)

@login_required(login_url='/corporateLogin/')
def corporateHistory(request):
    if not is_corporate_user(request.user):
        messages.error(request, {'status': 'error', 'message': 'Access forbidden for non-corporate users.'})
        return redirect('userDashboard','service')

    user = User.objects.get(email=request.user.email)
    corporate = CorporateDB.objects.get(user=request.user)
    services = ServiceType.objects.filter(profession=corporate.profession,corporateappointment__corporate=corporate).annotate(count=Count('corporateappointment'))
    threads = Thread.objects.by_user(user=user).prefetch_related('messages').order_by('-created_at')
    last_messages = []

    for thread in threads:
        last_message = thread.messages.aggregate(Max('timestamp'))['timestamp__max']
        last_messages.append({'thread_id': thread.id, 'last_message': last_message})

    appointments = CorporateAppointment.objects.filter(corporate=corporate,is_completed = True)
    context = {'user': user, 'corporate': corporate,'services': services, 'threads': threads, 'last_messages': last_messages, 'appointments': appointments}

    # print(services)
    # context = {'user': user, 'corporate': corporate,'services': services, 'threads': threads, 'last_messages': last_messages}
    return render(request, "corporateHistory.html", context)



#     corporate = CorporateDB.objects.get(user=request.user)
@login_required(login_url='/corporateLogin/')
def viewCorporateAppointments(request,service):
    print("pppppp")
    print(request)
    print(request.body)
    if not is_corporate_user(request.user):
        return HttpResponseForbidden("Access forbidden for non-corporate users.")

    user = User.objects.get(email=request.user.email)
    corporate = CorporateDB.objects.get(user=request.user)
    services = ServiceType.objects.filter(profession=corporate.profession,corporateappointment__corporate=corporate).annotate(count=Count('corporateappointment'))
    threads = Thread.objects.by_user(user=user).prefetch_related('messages').order_by('-created_at')
    last_messages = []

    for thread in threads:
        last_message = thread.messages.aggregate(Max('timestamp'))['timestamp__max']
        last_messages.append({'thread_id': thread.id, 'last_message': last_message})
    service = ServiceType.objects.get(alias=service)
    appointments = CorporateAppointment.objects.filter(corporate=corporate,serviceType=service,is_completed=False)
    context = {'user': user, 'corporate': corporate,'services': services, 'threads': threads, 'last_messages': last_messages, 'appointments': appointments}
    return render(request, "corporateDashboardService.html", context)


@login_required(login_url='/corporateLogin/')
def completeCorporateStatus(request):
    print("***************************sssssssssssssssssssssssss")
    print(request)
    if request.method == 'POST' and request.user.is_corporate:
        appointment_id = request.POST.get('appointment_id')
        try:
            appointment = CorporateAppointment.objects.get(id=appointment_id)
            if appointment.corporate_complete:
                appointment.corporate_complete = False
                appointment.is_completed = False
                message = 'unmarked'
            else:
                appointment.corporate_complete = True
                message = 'marked'
                if appointment.customer_complete:
                    appointment.is_completed = True
                    thread = Thread.objects.get(appointment=appointment)
                    thread.is_active = False
                    thread.save()

            appointment.save()
            message = {
            'status': 'success',
            'message': f'Appointment {message} as completed!'
            }
            messages.success(request,  message)
            return redirect(request.META.get('HTTP_REFERER', 'corporateDashboard')) 
        except CorporateAppointment.DoesNotExist:
            message = {
            'status': 'error',
            'message': 'Something went wrong! Please try again!'
            }
            messages.success(request,  message)
            return redirect('corporateDashboard') 
    else:
        message = {
        'status': 'error',
        'message': 'Method not allowed!'
        }   
        messages.success(request,  message)
        return redirect('corporateDashboard')  

# @login_required(login_url='/auth/loginuser/')
# def completeCustomerStatus(request):
#     print("***************************sssssssssssssssssssssssss")
#     print(request)
#     if request.method == 'POST' and request.user.is_customer:
#         appointment_id = request.POST.get('appointment_id')
#         rating = Decimal(request.POST.get('rating'))
#         try:
#             with transaction.atomic():
#                 appointment = CorporateAppointment.objects.get(id=appointment_id)
#                 corporate = CorporateDB.objects.get(cid =  appointment.corporate.cid)
                
#                 existing_ratings = CorporateDB.objects.filter(cid =  appointment.corporate.cid).exclude(rating=None)
                
#                 if existing_ratings.exists():
#                     current_avg_rating = existing_ratings.aggregate(avg_rating=Avg('rating'))['avg_rating']
#                     total_ratings = existing_ratings.count()
#                     new_avg_rating = ((current_avg_rating * total_ratings) + rating) / (total_ratings + 1)
#                 else:
#                     new_avg_rating = rating

#                 corporate.rating = new_avg_rating
#                 corporate.save()

#                 appointment.customer_complete = True
#                 appointment.save()

#                 message = {
#                 'status': 'success',
#                 'message': 'Appintment marked as completed!'
#                 }
#                 messages.success(request,  message)
#                 return redirect('userDashboard','service')  # Replace 'success_page' with the URL name of your success page
#         except CorporateAppointment.DoesNotExist:
#             message = {
#             'status': 'error',
#             'message': 'Something went wrong! Please try again!'
#             }
#             messages.success(request,  message)
#             return redirect('userDashboard','service')  # Replace 'success_page' with the URL name of your success page
#     else:
#         message = {
#         'status': 'error',
#         'message': 'Method not allowed!'
#         }   
#         messages.success(request,  message)
#         return redirect('viewCorporateAppointments','service')  # Replace 'success_page' with the URL name of your success page
    
    

@login_required(login_url='/auth/loginuser/')
def completeCustomerStatus(request):
    if request.method == 'POST' and request.user.is_customer:
        appointment_id = request.POST.get('appointment_id')
        rating = Decimal(request.POST.get('rating'))
        try:
            with transaction.atomic():
                appointment = CorporateAppointment.objects.get(id=appointment_id)
                corporate = CorporateDB.objects.get(cid=appointment.corporate.cid)

                # Retrieve existing ratings for the corporate
                total_ratings = corporate.total_ratings
                if total_ratings == 0:
                    corporate.rating = rating
                else:
                    current_rating = corporate.rating
                    new_avg_rating = ((total_ratings*current_rating)+rating)/(total_ratings+1)
                    corporate.rating = new_avg_rating
                corporate.total_ratings = total_ratings + 1  # Increment total ratings
                corporate.save()

                appointment.customer_complete = True
                
                if appointment.corporate_complete:
                    appointment.is_completed = True
                    thread = Thread.objects.get(appointment=appointment)
                    thread.is_active = False
                    thread.save()
                
                appointment.save()
                message = {
                    'status': 'success',
                    'message': 'Appointment marked as completed!'
                }
                messages.success(request, message)
                return redirect('userDashboard', 'service')  # Redirect to success page
        except CorporateAppointment.DoesNotExist:
            message = {
                'status': 'error',
                'message': 'Something went wrong! Please try again!'
            }
            messages.error(request, message)
    else:
        message = {
            'status': 'error',
            'message': 'Method not allowed!'
        }
        messages.error(request, message)

    return redirect('viewCorporateAppointments', 'service')  # Redirect to view appointments page


@login_required(login_url='/corporateLogin/')
def checkReferralCode(request, referralCode):
    code = referralCode
    try:
        referralCode = GeneratedCode.objects.get(code=code)
    except GeneratedCode.DoesNotExist:
        return JsonResponse({"status": False, "message": "Code not found!"})
    
    if referralCode.is_redeemed:
        return JsonResponse({"status": False, "message": "Code already redeemed!"})
    if referralCode.expiration_datetime and referralCode.expiration_datetime < timezone.now():
        referralCode.is_expired = True
        referralCode.save()
        return JsonResponse({"status": False, "message": "Code has expired!"})
    else:
        return JsonResponse({"status": True, "message": "Verified!"})

@login_required(login_url='/corporateLogin/')
def corporateProfileForm(request):
    if not is_corporate_user(request.user):
        return HttpResponseForbidden("Access forbidden for non-corporate users.")

    corporate_db = CorporateDB.objects.get(user=request.user)
    if request.method == 'POST':

        print("dfcgvhbjnkfcvgbhnjmkgvbhnj ********************************")
        company_name = request.POST.get('companyName')
        experience = request.POST.get('experience')
        address = request.POST.get('address')
        pan = request.POST.get('pan')
        aadhar = request.POST.get('aadhar')
        pincode = request.POST.get('pincode')
        profile_pic_file = request.FILES.get('profilePic')
        
        alternate_phone = request.POST.get('alternatePhone')

        corporate_db.companyName = company_name
        corporate_db.experience = experience
        corporate_db.address = address
        corporate_db.pincode = pincode
        corporate_db.aadhar = aadhar
        corporate_db.pan = pan
        corporate_db.alternatePhone = alternate_phone

        if profile_pic_file:
            corporate_db.profilePic = profile_pic_file
            img = Image.open(profile_pic_file)
            output_io = BytesIO()
            img.save(output_io, format='JPEG', quality=60)
            output_io.seek(0)
            corporate_db.profilePic.save(profile_pic_file.name, content=output_io)

        corporate_db.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('corporateDashboard')
    else:
        if not corporate_db.companyName == None:
            data = {
            'companyName': corporate_db.companyName,
            'experience': corporate_db.experience,
            'address': corporate_db.address,
            'pincode': corporate_db.pincode,
            'aadhar': corporate_db.aadhar,
            'pan': corporate_db.pan,
            'alternatePhone': corporate_db.alternatePhone,
            'profilePic': corporate_db.profilePic
            }
        else:
            data = {}
        print("gadbad")
    return render(request, 'corporateProfile.html', {'data': data})

def corporateLogin(request):
    if request.user.is_authenticated and request.user.is_corporate:
        return redirect('corporateDashboard')
    
    if request.method == 'POST':
        
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email)
        print(password)
        try:
            corporate = User.objects.get(email=email)
            if corporate.is_corporate == False:
                messages.error(request, "Unauthorized access!")
                return redirect('corporateLogin')
        except:
            messages.add_message(request, messages.INFO, "User does not exist")
            print("User does not exist")
            return render(request, 'corporateLogin.html')
        user = authenticate(request, email = email, password = password)    
        
        if user is not None and user.is_corporate:
            login(request, user)
            print("logged in")
            return redirect('corporateDashboard')
        else:
            messages.error(request,  "Invalid credentials")
            
    return render(request,'corporateLogin.html')



def corporateLogout(request):
  logout(request)
  return redirect('home')

@login_required(login_url="/corporateLogin/")
def verifyReferralCode(request):
    print("******IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII ****")
    if not is_corporate_user(request.user):
        return HttpResponseForbidden("Access forbidden for non-corporate users.")

    if request.method == 'POST'and request.user.is_corporate:
        try:
            referralCode = request.POST.get('referralCode')
        except:
            referralCode = None
        print(referralCode)    
        disc = 0
        if referralCode is not None:
            try:
                code_obj = GeneratedCode.objects.get(code=referralCode)
                if code_obj.expiration_datetime and code_obj.expiration_datetime < timezone.now():
                    code_obj.is_expired = True
                    code_obj.save()
                    disc = 0
                elif not code_obj.is_redeemed:
                    disc = int(code_obj.percentage.strip('%'))
                else:
                    disc = 0
            except GeneratedCode.DoesNotExist:
                disc = 0
        print("********************************")
        print(disc)
        
        discount = True if disc != 0 else False
        subscriptions = SubscriptionType.objects.all().values()
        print(subscriptions)
        if discount:
            for subscription in subscriptions:
                subscription["new_price"] = subscription["default_price"]-((subscription["default_price"]*disc)/100)
        print(subscriptions)        
        print("tebsdkcbsvkjsvsdbljvndl")
        print(type(referralCode))
        context = {"discount": discount, "discount_percentage": 1000, "subscriptions": subscriptions, "referralCode":referralCode}       
        return render(request,"chooseSubscription.html",context)
    return HttpResponseBadRequest("Invalid request")


@login_required(login_url="/corporateLogin/")        
def initiatePaymentRequest(request):
    if not is_corporate_user(request.user):
        return HttpResponseForbidden("Access forbidden for non-corporate users.")

    if request.method == 'POST' and request.user.is_corporate:
        user = request.user
        corporate = CorporateDB.objects.get(user=user)
        default_price = request.POST.get('default_price')
        value = request.POST.get('value')
        referralCode = request.POST.get('referralCode')
        new_price = request.POST.get('new_price')
        if referralCode == 'None' or referralCode == '':
            referralCode = None
        if new_price == '' or new_price == None:
            amount = default_price
        else:
            amount = default_price
        print("above all")
        print(request.POST.get('referralCode'))
        print(type(request.POST.get('referralCode')))
        
        print(amount, value, referralCode)
        print(type(amount), type(referralCode), type(value))
        try:
            subType = SubscriptionType.objects.get(value=value)
        except:                        
            messages.error(request,  "Something went wrong!")
        print(subType)
        print(type(None))
        print(type(referralCode))
        
        context = {}
        context['amount'] = amount
        amount = int(float(amount))*100
        currency = 'INR'
        data = { "amount": amount, "currency": currency}
        razorpay_order = razorpay_client.order.create(data=data)

        razorpay_order_id = razorpay_order['id']
        callback_url = 'https://test-deploy-klbw.onrender.com/payment-handler/'
        context['razorpay_order_id'] = razorpay_order_id
        context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
        context['razorpay_amount'] = amount
        context['currency'] = "INR"
        context['callback_url'] = callback_url
        paymentObj = CorporatePayments.objects.create(
            amount = amount,
            cid=corporate,
            subscription_type = subType,
            referralCode=referralCode,
            razorpay_order_id = razorpay_order_id
        )
        return render(request, "confirmPayment.html",context)

# def corporateRegistration(request):
#     context = {"professions": Professions.objects.all()}
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         businessName = request.POST.get('businessName')
#         profession_name = request.POST.get('profession')
#         email = request.POST.get('email')
#         phone = request.POST.get('phone')
#         if(not name or not email or not phone or not businessName or not profession_name):
#             return HttpResponseBadRequest()
#         try:
#             referralCode = request.POST.get('referralCode')
#         except:
#             referralCode = None
            
#         disc = 0
#         if referralCode is not None:
#             try:
#                 code_obj = GeneratedCode.objects.get(code=referralCode)
#                 if not code_obj.is_redeemed:
#                     disc = int(code_obj.percentage.strip('%'))
#                 else:
#                     disc = 0
#             except GeneratedCode.DoesNotExist:
#                 disc = 0
#         profession = Professions.objects.get(name=profession_name)
#         profession_mapping = {
#                 'CA': 'C',
#                 'ARCHITECT/VALUER': 'E',
#                 'ADVOCATE/LEGAL ADVISOR': 'L',
#                 'DSA': 'D',
#                 'OTHERS': 'O',
#             }
#         profession_code = profession_mapping.get(profession.name, 'O')
#         random_number = str(random.randint(1, 9999)).zfill(4)
#         generated_id = f'C{random_number}{profession_code}{name[0]}'
#         while CorporateDB.objects.filter(cid=generated_id).exists():
#             random_number = str(random.randint(1, 9999)).zfill(4)
#             generated_id = f'C{random_number}{profession_code}{name[0]}'
        
#         amount = (25000-((25000*disc)/100))*100
#         currency = 'INR'
#         data = { "amount": amount, "currency": "INR"}
#         razorpay_order = razorpay_client.order.create(data=data)

#         razorpay_order_id = razorpay_order['id']
#         callback_url = 'http://127.0.0.1:8000/payment-handler/'
#         context = {"professions": Professions.objects.all()}
#         context['razorpay_order_id'] = razorpay_order_id
#         context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
#         context['razorpay_amount'] = amount
#         context['currency'] = "INR"
#         context['callback_url'] = callback_url
#         corporate = CorporateDB.objects.create(
#             cid=generated_id,
#             name=name,
#             businessName=businessName,
#             profession=profession,
#             email=email,
#             phone=phone,
#             referralCode=referralCode,
#             razorpay_order_id = razorpay_order_id
#         )
#         return render(request, "confirmPayment.html",context)
#     else:
#         return render(request, "corporateRegistration.html",context)


@csrf_exempt
def paymenthandler(request):
    if not is_corporate_user(request.user):
        return HttpResponseForbidden("Access forbidden for non-corporate users.")

    if request.method == "POST":
            razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            razorpay_signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            paymentObject = CorporatePayments.objects.get(razorpay_order_id = razorpay_order_id)
            corporate = paymentObject.cid
            # server_order_id = corporate.razorpay_order_id
            result = razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
            })
            if result is True:
                corporate.has_paid = True
                corporate.is_active = True
                noOfDays = int(paymentObject.subscription_type.value) * 30
                current_date = datetime.now().date()
                endDate = current_date + timedelta(days=noOfDays)
                corporate.active_till = endDate
                corporate.subscription_type = paymentObject.subscription_type
                corporate.save()
                paymentObject.razorpay_order_id = razorpay_order_id,
                paymentObject.razorpay_payment_id = razorpay_payment_id,
                paymentObject.razorpay_signature = razorpay_signature
                paymentObject.verified = True
                if paymentObject.referralCode is not None and not paymentObject.referralCode == '':
                    try:
                        paymentObject.referralUsed = True
                        code_obj = GeneratedCode.objects.get(code = corporate.referralCode)
                        code_obj.is_redeemed = True
                        code_obj.save()
                    except Exception as e:
                        print("Error",e)
                paymentObject.save()
            return redirect('corporateDashboard')          
    else:
        return HttpResponseBadRequest()


def GenerateCode(request):
    if request.method == 'POST' and request.user.is_superuser:
        code = request.POST.get('code')
        percentage = request.POST.get('percentage')
        GeneratedCode.objects.create(code=code, percentage=percentage)
        print("Created Successfully",code)
        return redirect('codegeneration')
    
    if request.user.is_superuser:
        unique_code = str(uuid.uuid4())[:8]
        return render(request, "generatecode.html", {'unique_code': unique_code})
    else:
        return render(request, "Error.html")
    
@login_required(login_url='/auth/loginuser/')
def loanBooking(request):
    if not is_customer(request.user):
        return HttpResponseForbidden("Access forbidden for non-customer users.")

    if request.method == 'POST':
        customer = request.user
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
        phone = request.POST.get('phone')
        loan_type = request.POST.get('loanType')
        monthly_salary= request.POST.get('monthlySalary')
        loan_amount = request.POST.get('loanAmount')
        
        # Convert monthly_salary to Decimal
        monthly_salary = float(monthly_salary)
        loan_amount = float(loan_amount)
        
        loanType = LoanType.objects.get(name=loan_type)
        # Calculate the annual salary
        try:
            monthly_salary = Decimal(monthly_salary)
            year_salary = monthly_salary * 12
        except Exception as e:
            year_salary = 0

        application = LoanDetail(
            customer=customer,
            name=name,
            email=email,
            address=address,
            pincode=pincode,
            phone=phone,
            loan_type=loanType,
            monthly_salary=monthly_salary,
            year_salary=year_salary,
            loan_amount=loan_amount,
        )
        try:
            application.save()
        except Exception as e:
            print(f"Error while saving data: {e}")
        return redirect ("userDashboard",'loan') 
    return render(request, "home.html")

@login_required(login_url='/auth/loginuser/')
def personalLoan(request):
    return render(request, "loanForms/personalLoanForm.html")

@login_required(login_url='/auth/loginuser/')
def educationLoan(request):
    return render(request, "loanForms/educationLoanForm.html")

@login_required(login_url='/auth/loginuser/')
def homeLoan(request):
    return render(request, "loanForms/homeLoanForm.html")

@login_required(login_url='/auth/loginuser/')
def twoWheelerLoan(request):
    return render(request, "loanForms/twoWheelerLoanForm.html")

@login_required(login_url='/auth/loginuser/')
def carLoan(request):
    return render(request, "loanForms/carLoanForm.html")


def loanPage(request):
    return render(request, "loanPage.html")

@login_required(login_url='/auth/loginuser/')
def usedCarLoan(request):
    return render(request, "loanForms/usedCarLoanForm.html")

def consultantServices(request):
    return render(request, "consultantServices.html")

def subServices(request,sub):
    profession = Professions.objects.get(alias=sub)
    services = ServiceType.objects.filter(profession=profession)
    return render(request, "subServices.html", {"services":services, "profession":profession})

# def viewProviders(request):
#     if request.method == 'GET':
#         service_name = request.GET.get('service_name')
#         service_price = request.GET.get('service_price')
#         service = ServiceType.objects.get(name=service_name)
#         profession = Professions.objects.get(name=service.profession)
#         corporates = CorporateDB.objects.filter(profession=profession,is_active=True)
#         return render(request, 'viewProviders.html', {"corporates": corporates ,'service': service})


@login_required(login_url='/auth/loginuser/')
def viewProviders(request):
    if not is_customer(request.user):
        return HttpResponseForbidden("Access forbidden for non-customer users.")

    if request.method == 'GET':
        service_name = request.GET.get('service_name')
        service_price = request.GET.get('service_price')
        location_filter = request.GET.get('location')
        
        service = ServiceType.objects.get(name=service_name)
        profession = Professions.objects.get(name=service.profession)
        locations = ['Delhi', 'Noida', 'Jhansi', 'Varanasi']
        # Filter corporates based on profession and location
        corporates = CorporateDB.objects.filter(profession=profession, is_active=True)
        if location_filter:
            corporates = corporates.filter(location=location_filter)
        for corporate in corporates:
            print(corporate.profilePic)
        return render(request, 'viewProviders.html', {"corporates": corporates, 'service': service, 'locations': locations, 'location_filter': location_filter})


@login_required(login_url="/auth/loginuser/")
def providerDetails(request, cid):
    if request.user.is_customer:
        cid = cid
        try:
            corporate = CorporateDB.objects.get(cid=cid)
        except:
            messages.error(request, "Corporate doesn't exist")
            return redirect("userDashboard.html",'service')
        return render(request, 'providerDetails.html',{'corporate':corporate})
    else:
        messages.error(request, "You are not allowed here")
        return redirect('corporateDashboard')
                    

@login_required(login_url="/auth/loginuser/")
def userDashboard(request, page):
    if request.user.is_customer:
        active = page
        user = request.user
        loans = user.loans.all()
        appointments = user.appointments.filter(is_paid=True, is_completed=False)
        pastAppointments = user.appointments.filter(is_paid=True, is_completed = True)
        threads = Thread.objects.by_user(user=user).prefetch_related('messages').order_by('-created_at')
        print(loans)
        print(appointments)
        context = {"user": user, "loans": loans, "appointments": appointments, "pastAppointments" : pastAppointments, "active": active, "threads": threads}
        print(context)
        return render(request, 'userDashboard.html', context)
    else:
        messages.error(request,  "You are not allowed to access that page.")
        return redirect('corporateDashboard')


@login_required(login_url="/auth/loginuser/")
def updateUserProfile(request):
    if not is_customer(request.user):
        return HttpResponseForbidden("Access forbidden for non-customer users.")
    if request.method == 'POST' and request.user.is_customer:
        try:
            user = request.user
            name = request.POST.get('name', '')
            address = request.POST.get('address', '')
            pincode = request.POST.get('pincode', '')
            phone = request.POST.get('phone', '')
            profilePic = request.FILES.get('profilepic', '')
            if UserDB.objects.filter(user=user).exists():
                userdb = UserDB.objects.get(user=user)
                with transaction.atomic():
                    user.name = name
                    user.phone = phone
                    user.save()
                    userdb.address = address
                    userdb.pincode=pincode
                    if profilePic:
                        userdb.profilePic=profilePic
                    userdb.save()
            else:
                with transaction.atomic():
                    user.name = name
                    user.phone = phone
                    UserDB.objects.create(user=user, address=address,pincode=pincode,  profilePic=profilePic)
            message = {
            'status': 'success',
            'message': 'Profile updated successfully!'
            }
            messages.error(request,  message)
            return redirect('userDashboard','service')
        except:
            message = {
            'status': 'error',
            'message': 'Something went wrong! Please try again!'
            }
            messages.error(request,  message)
            return redirect('consultantServices')
    elif request.method == 'GET' and request.user.is_customer:
        user = request.user
        if UserDB.objects.filter(user=user).exists():
            context = {'user': user, 'userdb':  UserDB.objects.get(user=user)}    
        else:
            context = {'user': user}
        
        return render(request, 'updateUserProfile.html',context)
    

            
                
                
            
            
            
            

@login_required(login_url="/auth/loginuser/")
def bookAppointment(request):
    if not is_customer(request.user):
        return HttpResponseForbidden("Access forbidden for non-customer users.")
    
    if request.method == 'POST' and request.user.is_customer:
        try:
            customer = request.user
            service = request.POST.get('service')
            cid = request.POST.get('cpid')
            if not service or not cid:
                print("hhhhh")
                messages.error(request,  "Something went wrong! Please try again!")
                return redirect(request.META.get('HTTP_REFERER', 'consultantServices'))
            serviceType = ServiceType.objects.get(name=service)
            corporate = CorporateDB.objects.get(cid=cid)
            context = {}
            context['amount'] = int(serviceType.price)
            amount = int(serviceType.price)*100            
            currency = 'INR'
            data = { "amount": amount, "currency": currency, "notes":{"customer_id":customer.id}}
            razorpay_order = razorpay_client.order.create(data=data)
            razorpay_order_id = razorpay_order['id']

            appointment=CorporateAppointment.objects.create(
                customer=customer,
                serviceType=serviceType,
                corporate=corporate,
                razorpay_order_id = razorpay_order_id
            )
            
            callback_url = 'https://test-deploy-klbw.onrender.com/appointmentPaymentHandler/'
            context['razorpay_order_id'] = razorpay_order_id
            context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
            context['razorpay_amount'] = amount
            context['currency'] = "INR"
            context['callback_url'] = callback_url
            context['appointment'] = appointment
            return render(request, 'appointmentConfirmation.html',context)
        except Exception as e:
            print("here's an error", e)
            message = {
            'status': 'error',
            'message': 'Something went wrong! Please try again!'
            }
            messages.error(request,  message)
            return redirect('consultantServices')
    else:
        message = {
            'status': 'error',
            'message': 'You are not allowed on this page.'
        }
        messages.error(request,  message)
        return redirect('consultantServices')

       
@csrf_exempt
def appointmentPaymentHandler(request):
    if not is_customer(request.user):
        return HttpResponseForbidden("Access forbidden for non-customer users.")

    if request.method == "POST":
            razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            razorpay_signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            appointment = CorporateAppointment.objects.get(razorpay_order_id = razorpay_order_id)
            result = razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
            })
            if result is True:
                with  transaction.atomic():
                    appointment.is_paid = True
                    appointment.save()
                    thread, created = Thread.objects.get_or_create(appointment=appointment, customer=appointment.customer, corporate=appointment.corporate.user)

                    initial_message = f"Appointment booked for {appointment.serviceType.name} with {appointment.corporate.businessName}."
                    ChatMessage.objects.create(thread=thread, sender=appointment.customer, message=initial_message)

                    appointmentPayment = AppointmentPayment.objects.create(
                        appointment=appointment,
                        amount=appointment.serviceType.price,
                        razorpay_order_id = razorpay_order_id,
                        razorpay_payment_id = razorpay_payment_id,
                        razorpay_signature = razorpay_signature,
                        verified = True
                    )
                messages.success(request, "Successfully booked the appointment!")
                return render(request, "appointmentSuccess.html",{"appointment":appointment})        
    else:
        return HttpResponseBadRequest()

