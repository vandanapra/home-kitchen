from django.urls import path
from .views import SendOTPView, VerifyOTPView, ProfileView,SendOTPViewviaWhatsapp,SignupView

urlpatterns = [
    path("signup/", SignupView.as_view()),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('send-otp-whatsapp/', SendOTPViewviaWhatsapp.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
