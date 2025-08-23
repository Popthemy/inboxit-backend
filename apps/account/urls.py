from django.urls import path
from . import views

urlpatterns = [
    path('signup/', view=views.RegisterView.as_view(), name='register_user'),
    path('signup/verify-email-otp/',
         view=views.EmailVerifyOTPView.as_view(), name='verify_email_otp'),
    path('signup/email-resend-otp/',
         view=views.EmailResendOTPView.as_view(), name='email_resend_otp'),
    path('login/', view=views.LoginView.as_view(), name='login_user'),
    path('signout/', view=views.LogoutView.as_view(), name='logout_user'),
    path('refresh/', view=views.TokenRefreshView.as_view(), name='token_refresh'),

    # forgotten password
    path('password-reset/', view=views.PasswordResetRequestOTPView.as_view(),
         name='password_reset'),
    path('password-reset/verify-password-otp/',view=views.PasswordResetVerifyView.as_view(), name='verify_password_otp'),
    path('users/<uuid:pk>/profiles/',views.ProfileView.as_view(),name='user_profiles'),

]
