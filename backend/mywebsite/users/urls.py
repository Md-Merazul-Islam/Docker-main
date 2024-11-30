

from django.urls import path
from .views import UserRegisterView, UserVerifyEmailView, UserLoginView, UserLogOutView, UserProfileUpdateView,SendOTPView, ResetPasswordView,VerifiedUserListView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('verify-email/', UserVerifyEmailView.as_view(), name='verify_email'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogOutView.as_view(), name='logout'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile_update'),
    path('send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('verified-users/', VerifiedUserListView.as_view(), name='verified-staff-superusers'),
]
