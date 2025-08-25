from django.urls import path
from .views import cookie_views


#works with adding token in the cookies
urlpatterns = [
    path('signup/', view=cookie_views.CookieRegisterView.as_view(), name='register_user'),
    path('signup/verify-email-otp/',
         view=cookie_views.CookieEmailVerifyOTPView.as_view(), name='verify_email_otp'),
    path('signup/email-resend-otp/',
         view=cookie_views.EmailResendOTPView.as_view(), name='email_resend_otp'),
    path('login/', view=cookie_views.CookieLoginView.as_view(), name='login_user'),
    path('me/', view=cookie_views.MeView.as_view(), name='user_details'),
    path('logout/', view=cookie_views.CookieLogoutView.as_view(), name='logout_user'),
    path('refresh/', view=cookie_views.CookieTokenRefreshView.as_view(), name='cookies_refresh'),

    # forgotten password
    path('password-reset/', view=cookie_views.PasswordResetRequestOTPView.as_view(),
         name='password_reset'),
    path('password-reset/verify-password-otp/',view=cookie_views.PasswordResetVerifyView.as_view(), name='verify_password_otp'),
    path('users/<uuid:pk>/profiles/',cookie_views.ProfileView.as_view(),name='user_profiles'),

]

"""
from .views import token_views

# showing token in the response
urlpatterns = [
    path('signup/', view=token_views.RegisterView.as_view(), name='register_user'),
    path('signup/verify-email-otp/',
         view=token_views.EmailVerifyOTPView.as_view(), name='verify_email_otp'),
    path('signup/email-resend-otp/',
         view=token_views.EmailResendOTPView.as_view(), name='email_resend_otp'),
    path('login/', view=token_views.LoginView.as_view(), name='login_user'),
    path('me/', view=token_views.MeView.as_view(), name='user_details'),
    path('signout/', view=token_views.LogoutView.as_view(), name='logout_user'),
    path('refresh/', view=token_views.TokenRefreshView.as_view(), name='token_refresh'),

    # forgotten password
    path('password-reset/', view=token_views.PasswordResetRequestOTPView.as_view(),
         name='password_reset'),
    path('password-reset/verify-password-otp/',view=token_views.PasswordResetVerifyView.as_view(), name='verify_password_otp'),
    path('users/<uuid:pk>/profiles/',token_views.ProfileView.as_view(),name='user_profiles'),

]"""
