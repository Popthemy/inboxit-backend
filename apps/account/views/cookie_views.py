'''
Here lies the view for auth using cookies that include JWT access and refresh tokens.
The response return tokens(access and refresh) in HTTP ONLY Cookies.
'''

from django.contrib.auth import get_user_model, authenticate
from django.http import Http404
from django.db import transaction
from django.conf import settings
from django.urls import reverse
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from apps.account.documentation.account.schemas import (
    register_user_doc, login_user_doc, logout_user_doc, email_verify_otp_doc, resend_email_otp_doc, password_reset_otp_doc,
    password_reset_verify, profile_doc, refresh_token_doc
)
from apps.account.serializers import (
    UserSerializer, LoginSerializer, LogoutSerializer, OTPSerializer, EmailSerializer,
    PasswordResetSerializer, ProfileSerializer
)
from apps.account.utils import OTPService, send_email_with_url,set_auth_cookies, clear_auth_cookies
from apps.account.permissions import IsAnonymous, IsProfileOwnerOrAdmin
from apps.account.models import Profile

User = get_user_model()

OTP_EMAIL_EXPIRY_TIME = settings.OTP_EMAIL_EXPIRY_TIME
OTP_PASSWORD_EXPIRY_TIME = settings.OTP_PASSWORD_EXPIRY_TIME
FRONTEND_URL = settings.FRONTEND_URL

class CookieSetCsrfTokenView(GenericAPIView):
    '''Forces a CSRF token to be set and return it '''
    def get(self,request):
        token = get_token(request)
        return Response({'csrf_token':token})


class CookieRegisterView(GenericAPIView):
    '''
    After signup user is directed to enter the otp they receive in their mail to verify their account.
    Endpoint is only open to non-user.
    '''
    serializer_class = UserSerializer
    permission_classes = [IsAnonymous]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'register'

    @register_user_doc
    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        try:
            with transaction.atomic():
                serializer.is_valid(raise_exception=True)
                user = serializer.save()

                email = user.email
                purpose = 'email'

                otp = OTPService.generate_and_store_otp(
                    email=email, purpose=purpose)

                send_email_with_url(email=email,
                                    subject='Verify Email OTP',
                                    otp_code=otp,
                                    purpose=purpose,
                                    url_name=f"{FRONTEND_URL}/signup/verify_email_otp/",
                                    template='account/verification_otp.html'
                                    )
                data = {
                    'status': 'success',
                    'message': 'Registration successful, please check your email to verify your account. '
                    'If you didn\'t receive the OTP, you can use the resend verification link.',
                    'data': serializer.data,
                    'resend verification link': f"{FRONTEND_URL}{reverse('email_resend_otp')}",
                }
                return Response(data=data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error_message': f'Account creation failed {e}'},
                            status=status.HTTP_400_BAD_REQUEST)


class CookieEmailVerifyOTPView(GenericAPIView):
    '''
    Verify the otp sent to the user email.
    Get user email in the url and verify if the user and the mail are valid and
    verifies user and they can login
    '''
    serializer_class = OTPSerializer

    @email_verify_otp_doc
    def post(self, request):
        email = request.query_params.get('email').strip()
        otp = request.data.get('otp').strip()

        if not email or not otp:
            return Response(
                {'message': 'Either email missing in link or OTP not provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)

            is_verified = OTPService.verify_and_delete_otp(
                email=email, raw_otp=otp, purpose='email')

            if not is_verified:
                return Response(
                    {'message': 'Invalid or expired OTP. Generate a new one.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.is_active = True
            user.save()

            serializer = UserSerializer(user)
            tokens = user.get_jwt_tokens
            res = Response(data={
                'status': 'Success',
                'message': 'Email verified successfully!',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

            return set_auth_cookies(res, tokens)
        except User.DoesNotExist:
            return Response(
                {'message': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class EmailResendOTPView(GenericAPIView):
    '''Generate and send new OTP when previous one expires'''
    serializer_class = EmailSerializer

    @resend_email_otp_doc
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response(
                {"message": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            # check user exists
            user = User.objects.get(email=email)
            print(user)

            # if user.is_active:
            #     return Response(
            #         {"message": "User is already verified. You can login directly"},
            #         status=status.HTTP_400_BAD_REQUEST
            #     )

            # Generate and store new OTP
            new_otp = OTPService.generate_and_store_otp(
                email=email,
                purpose='email'
            )

            # send mail
            send_email_with_url(email=email,
                                subject='Resend Email Verify OTP',
                                otp_code=new_otp,
                                purpose='email',
                                url_name=f"{FRONTEND_URL}/verify_email_otp/",
                                template='account/verification_otp.html'
                                )

            return Response(
                {"message": "New OTP generated and sent to mail successfully "
                    "If you didn\'t receive the OTP, because of bad connection you should retry "},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'message': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": f"Failed to resend OTP: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CookieLoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [IsAnonymous]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    @login_user_doc
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})

        try:
            serializer.is_valid(raise_exception=True)
            user = self.login_user(serializer.validated_data)

            serializer = UserSerializer(user)
            tokens = user.get_jwt_tokens
            res = Response(data={
                'status': 'Success',
                'message': 'Login successfully!',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

            return set_auth_cookies(res, tokens)
        except Exception as e:
            return Response(data={
                'status': 'Error',
                'message': 'Login Unsuccessful',
                'data': str(e)},
                status=status.HTTP_400_BAD_REQUEST)

    def login_user(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']

        user = authenticate(
            request=self.request, username=email, password=password)

        if user is None:
            user = User.objects.filter(email=email).first()
            if not user.is_active:
                raise ValidationError(
                    'Verify you email to access your account!')
            raise ValidationError('Invalid Details!')
        return user


@refresh_token_doc
class CookieTokenRefreshView(GenericAPIView):
    """ Allows a user to get new access token after their token has expired."""
    serializer_class = LogoutSerializer # placeholder

    def post(self, request,*args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response({'detail':'Refresh token not provided'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            token = RefreshToken(refresh_token)
            tokens = {
                'access_token':str(token.access_token),
                'refresh_token': str(token)
            }
            res = Response({'message':'login refreshed'},status=status.HTTP_200_OK)

            return set_auth_cookies(res,tokens)
        except Exception as e:
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


class MeView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return super().get_queryset()

    def get(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(request.user.profile)
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({'status': 'profile not found!'}, status=status.HTTP_404_NOT_FOUND)


class CookieLogoutView(GenericAPIView):
    '''Log out and to clear cookies'''

    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    @logout_user_doc
    def post(self, request, *args, **kwargs):

        try:
            refresh_token =request.COOKIES.get('refresh_token')
            if refresh_token is None:
                return Response({"detail": "Refresh token not provided"}, status=status.HTTP_401_UNAUTHORIZED)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            res = Response(data={'message': 'Logout successful'},
                            status=status.HTTP_205_RESET_CONTENT)
            return clear_auth_cookies(res)
        except Exception as e:
            return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestOTPView(GenericAPIView):
    """
    create a password reset and send user OTP
    POST /api/auth/password-reset/ { "email": "user@example.com" }
    """
    serializer_class = EmailSerializer

    @password_reset_otp_doc
    def post(self, request):

        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
            otp = OTPService.generate_and_store_otp(email, 'password')

            # Send email with password reset template
            send_email_with_url(
                email=email,
                subject='Password Request Confirmation',
                otp_code=otp,
                purpose='password',
                url_name=f"{FRONTEND_URL}/verify_password_otp/",
                template='account/password_reset_otp.html'
            )
            return Response(
                {"message": "Password reset OTP sent if email exists. "
                 "Check email and follow the link or retry"},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"message": "If this email exists, we've sent a reset code"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"message": f"Failed to send OTP: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@password_reset_verify
class PasswordResetVerifyView(GenericAPIView):
    """Verify OTP and set new password"""
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = request.query_params.get('email').strip()
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        # Verify OTP
        if not OTPService.verify_and_delete_otp(
            email=email, raw_otp=otp, purpose='password'
        ):
            return Response(
                {"message": "Invalid or expired OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update password
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            return Response(
                {"message": "Password updated successfully. Kindly login"},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"message": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": f"Password reset failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


@profile_doc
class ProfileView(GenericAPIView):
    '''This endpoint is available to only authenticated user.
    Ordinary user can view their profile while admin can view anyone's profile.
    e.g uuid:b325169d-cc1c-418a-acdd-ca135ea9a038, 77771db5-7a45-4b95-85da-fee53d9d11c3
    '''
    permission_classes = [IsProfileOwnerOrAdmin]
    serializer_class = ProfileSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if self.request.user.is_staff or str(self.request.user.id) == str(pk):
            return Profile.objects.filter(user_id=pk)
        return Profile.objects.none()

    def get(self, request, *args, **kwargs):
        '''retrieve their own profile include their id in the url path'''
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """
        Update profile details.
        """
        profile = self.get_object()
        if profile is None:
            return Response({'status': 'profile not found!'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(
            instance=profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'status': 'success',
            'message': 'successfully updated',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        profile = self.get_object().delete()
        print(profile)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_context(self):
        try:
            profile = self.get_object()
            return {'user': profile.user}
        except Http404:
            return super().get_serializer_context()
