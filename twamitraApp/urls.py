from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("about/", views.about, name="about"),
    path("corporate-registration/", views.corporateRegistration, name="corporate-registration"),
    path("dashboard/<str:page>/", views.userDashboard, name="userDashboard"),
    path("updateProfile", views.updateUserProfile, name="updateUserProfile"),
    path("save_generated_code/", views.GenerateCode, name="codegeneration"),
    path("loanBooking/",views.loanBooking,name="loanBooking"),
    path("loanPage/",views.loanPage,name="loanPage"),
    path("payment-handler/",views.paymenthandler,name="paymenthandler"),
    path("carLoan/",views.carLoan,name="carLoan"),
    path("personalLoan/",views.personalLoan,name="personalLoan"),
    path("homeLoan/",views.homeLoan,name="homeLoan"),
    path("educationLoan/",views.educationLoan,name="educationLoan"),
    path("usedCarLoan/",views.usedCarLoan,name="usedCarLoan"),
    path("twoWheelerLoan/",views.twoWheelerLoan,name="twoWheelerLoan"),
    path("consultantServices/",views.consultantServices,name="consultantServices"),
    path("subServices/<str:sub>/",views.subServices,name="subServices"),
    path("corporateDashboard/",views.corporateDashboard,name="corporateDashboard"),
    path("corporateDashboard/<str:service>/",views.viewCorporateAppointments,name="viewCorporateAppointments"),
    path("corporateHistory/",views.corporateHistory,name="corporateHistory"),

    path("corporateLogin/",views.corporateLogin,name="corporateLogin"),
    path("corporateLogout/",views.corporateLogout,name="corporateLogout"),
    path("checkReferralCode/<str:referralCode>/",views.checkReferralCode,name="checkReferralCode"),
    path("verifyReferralCode/", views.verifyReferralCode,name="verifyReferralCode"),
    path("initiatePaymentRequest/",views.initiatePaymentRequest,name="initiatePaymentRequest"),
    path("corporateProfileForm/",views.corporateProfileForm,name="corporateProfileForm"),
    path("viewProviders/",views.viewProviders,name="viewProviders"),
    path("providerDetails/<str:cid>/",views.providerDetails,name="providerDetails"),
    path("bookAppointment/",views.bookAppointment,name="bookAppointment"),
    path("completeCorporateStatus/",views.completeCorporateStatus,name="completeCorporateStatus"),
    path("completeCustomerStatus/",views.completeCustomerStatus,name="completeCustomerStatus"),

    
    path("appointmentPaymentHandler/",views.appointmentPaymentHandler,name="appointmentPaymentHandler")
]
