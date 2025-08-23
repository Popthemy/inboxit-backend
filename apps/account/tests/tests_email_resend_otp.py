from rest_framework.test import APITestCase, override_settings
from rest_framework import status
from django.conf import settings
from django.urls import reverse
from apps.account.models import VerifyOTP
from django.contrib.auth import get_user_model
from apps.account.utils import OTPService

User = get_user_model()


@override_settings(EMAIL_BACKEND='django.core.mail.filebased.EmailBackends',
                   EMAIL_FILE_PATH=f'{settings.MEDIA_ROOT}/email_tests/')
class TestResendEmailOTP(APITestCase):
    def setUp(self):
        self.resend_url = reverse('email_resend_otp')
        self.user_data = {
            "email": "test@gmail.com",
            "first_name": "test",
            "last_name": "user",
            "password": "password@123",
            "confirm_password": "password@123"
        }
        self.user = User.objects.create_user(is_active=False,**self.user_data)
        self.otp = OTPService.generate_and_store_otp(email=self.user_data['email'],purpose='email')

      # def test_resend_otp_to_mail_return_200(self):
          
