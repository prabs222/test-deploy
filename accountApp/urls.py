from django.contrib import admin
from django.urls import path,include
from accountApp import views
urlpatterns = [
    
    path("registeruser/",views.registeruser,name="register"),
    path("loginuser/",views.loginuser,name="login"),
    path("dashboard/",views.dashboard,name="dashboard"),
    path("logoutuser/",views.logoutuser,name="logout"),
    path("dashboard/",views.dashboard,name="dashboard"),
]