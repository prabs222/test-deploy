import re
from django.shortcuts import render,HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate , login
from accountApp.models import User
from django.contrib import messages
from twamitraApp.forms import FormWithCaptcha

def dashboard(request):
  return render(request, 'home.html')

def registeruser(request):
    form = FormWithCaptcha()
    if request.method == "POST":
        email = request.POST.get("email",None)
        password1 = request.POST.get("password1",None)
        password2 = request.POST.get("password2",None)
        captchaForm = FormWithCaptcha(request.POST)
        if(captchaForm.is_valid()):
            print(email)
            print(password1)
            print(password2)
            if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", password1):
                messages.error(request, {'status': 'error', 'message': 'Password validations failed. Please make sure your password is at least 8 characters long and contains at least one digit, one special character, and one uppercase letter.'})
                return render(request, "register.html", {"form": form})
            if(password1 != password2):
                messages.success(request, {'status': 'error','message': 'Password mismatch!'})
                return render( request, "register.html", {"form":form}) 
            
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                messages.error(request, {'status': 'error', 'message': 'Invalid email format. Please enter a valid email address.'})
                return render(request, "register.html", {"form":form})

            allowed_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com', 'aol.com', 'protonmail.com', 'zoho.com', 'mail.com', 'yandex.com', 'gmx.com', 'live.com', 'inbox.com', 'fastmail.com', 'tutanota.com', 'rocketmail.com', 'rediffmail.com', 'lycos.com', 'mail.ru', 'cox.net', 'verizon.net', 'att.net', 'sbcglobal.net', 'earthlink.net', 'charter.net', 'optonline.net', 'mailinator.com', 'gmx.us', 'juno.com', 'netzero.net', 'hushmail.com', 'runbox.com', 'disroot.org', 'riseup.net', 'tormail.org', 'keemail.me']
            domain = email.split('@')[-1]
            if domain not in allowed_domains:
                messages.error(request, {'status': 'error', 'message': 'Invalid email domain. Please use an email from a valid email service provider.'})
                return render(request, "register.html", {"form":form})
               
            try:
                user = User.objects.create_user(username=email, email=email,password=password1,is_customer=True)
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            except:
                messages.success(request, {'status': 'error','message': 'Username already Taken! Try With another Username...'})
                return render( request, "register.html", {"form":form})
            return redirect ('home')
        else:
            message = {
            'status': 'error',
            'message': 'reCAPTCHA validation failed.'
            }
            messages.error(request, message)    
    return render(request, "register.html", {"form": form})

def loginuser(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email)
        print(password)
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, {'status':'error','message':'User does not exist'})
            return render(request,'login.html')
        if user.is_corporate:
            messages.error(request, {'status':'error','message':'This is user login page.'})
            return render(request,'login.html')
        user = authenticate(request, email = email, password = password)    
        
        if user is not None:
              message ={
                  'status':'success',
                  'message':'Logged in successfully'
              }
              messages.success(request, message)
              login(request, user)
              print("logged in")
              return redirect('userDashboard', 'service')
        else:
            messages.error(request,  "Invalid credentials")
          
    return render(request,'login.html')



def logoutuser(request):
    logout(request)
    return redirect('home')


def dashboard(request):
    return render (request, "dashboard.html")


