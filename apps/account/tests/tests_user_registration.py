from rest_framework.test import APITestCase, override_settings
from django.urls import reverse
from django.conf import settings
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.account.models import VerifyOTP
import os
import time
import re


User = get_user_model()


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.filebased.EmailBackend',
    EMAIL_FILE_PATH=f'{settings.MEDIA_ROOT}/emails_tests/'
)
class TestUserRegistration(APITestCase):
    def setUp(self):
        self.reg_url = reverse('register_user')
        self.verify_url = reverse('email_resend_otp')
        self.email_file_path = settings.EMAIL_FILE_PATH

        self.user_data = {
            "email": "test@gmail.com",
            "first_name": "test",
            "last_name": "user",
            "password": "password@123",
            "confirm_password": "password@123"
        }

    def test_user_registration_and_verification(self):
        '''
        Test valid user creation,
        check otp is created and stored,
        This is an  integration test!! both signup and 
        '''
        response = self.client.post(self.reg_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('success' in response.data['status'])
        self.assertTrue(self.verify_url in response.data['resend verification link'])

        user = User.objects.get(email=self.user_data['email'])
        self.assertFalse(user.is_active)

        otp = VerifyOTP.objects.get(
            email=self.user_data['email'], purpose='email')
        self.assertTrue(otp.otp)

        time.sleep(0.5)

        email_files = os.listdir(self.email_file_path)
        self.assertEqual(len(email_files), 1,
                         f'no email found in the dir{self.email_file_path}')
        email_file_path = os.path.join(self.email_file_path, email_files[0])

        with open(email_file_path, 'r') as lines:
            email_content = lines.read()

        html_start = email_content.find('<!DOCTYPE html>')
        html_body = email_content[html_start:] if html_start != - \
            1 else email_content

        otp_match = re.search(r'<div[^>]*>\s*([0-9]{4,8})\s*</div>', html_body)
        otp = otp_match.group(1) if otp_match else None
        self.assertIsNotNone(otp, 'OTP not found with regex')

        # verify user with their otp token
        verification_link_match = re.search(r'(http[s]?://[^\s]+)</p>', email_content)
        verification_link = verification_link_match.group(1) if verification_link_match else None
        self.assertIsNotNone(verification_link, 'verification_link not found with regex')

        # now verify a user and check their status
        response = self.client.post(verification_link, {'otp': otp})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['token'])

        user = User.objects.get(email=self.user_data['email'])
        self.assertTrue(user.is_active)

    def test_email_missing_return_400(self):
        self.user_data['email'] = ''

        response = self.client.post(self.reg_url,self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email',response.data['error_message'])

    def test_password_missing_return_400(self):
        self.user_data['password'] = ''

        response = self.client.post(self.reg_url,self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password',response.data['error_message'])

    def test_confirm_password_missing_return_400(self):
        self.user_data['confirm_password'] = ''

        response = self.client.post(self.reg_url,self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password',response.data['error_message'])

    def test_password_miss_match_return_400(self):
        self.user_data['password'] = 'password123'

        response = self.client.post(self.reg_url,self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('doesn\'t match',response.data['error_message'])

    def test_weak_password_match_return_400(self):
        self.user_data['password'] = 'password123'
        self.user_data['confirm_password'] = 'password123'
        response = self.client.post(self.reg_url,self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password is too common',response.data['error_message'])

        self.user_data['password'] = 'test'
        self.user_data['confirm_password'] = 'test'
        response = self.client.post(self.reg_url,self.user_data)
        self.assertIn('password is too short',response.data['error_message'])

    def tearDown(self):
        try:
            for filename in os.listdir(self.email_file_path):
                os.remove(os.path.join(self.email_file_path, filename))
            os.rmdir(self.email_file_path)
        except Exception as e:
            pass


