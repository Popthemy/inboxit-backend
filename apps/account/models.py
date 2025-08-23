from uuid import uuid4
from django.db import models, IntegrityError
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.conf import settings
from django_lifecycle import LifecycleModelMixin, hook, AFTER_UPDATE, AFTER_CREATE
from django_lifecycle.conditions import WhenFieldValueIs,WhenFieldValueWas
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.response import Response
from rest_framework import status
from .manager import CustomBaseUserManager


class VerifyOTP(models.Model):

    PURPOSE_CHOICES = [
        ('email', 'Email Verification'),
        ('password', 'Password Reset'),
    ]
    email = models.EmailField()
    otp = models.CharField(max_length=64)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['email', 'purpose']),]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.purpose} OTP for {self.email}"


class CustomUser(LifecycleModelMixin, AbstractUser):
    '''email, password, first name, last name, dob, age'''
    id = models.UUIDField(default=uuid4, primary_key=True,unique=True, editable=False)
    username = None
    email = models.EmailField(unique=True)
    agree_to_privacy_policy = models.BooleanField(default=False)

    objects = CustomBaseUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return self.get_full_name()

    @hook(AFTER_UPDATE,
          condition=WhenFieldValueWas('is_active', False) & WhenFieldValueIs('is_active', True))
    def create_profile(self):
        try:
            Profile.objects.get_or_create(
                user=self, email=self.email, first_name=self.first_name, last_name=self.last_name)
            # Profile.objects.create(user=self, email=self.email, first_name=self.first_name, last_name=self.last_name)
        except Exception as e:
            # print(f'user has a previous  profile not a new user: {self.email}, error:{str(e)}')
            pass



    @property
    def get_jwt_tokens(self):
        """Get both the refresh and access token for user"""

        try:
            refresh = RefreshToken.for_user(user=self)

            return {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }

        except TokenError as e:
            data = {'status': 'error', 'message': str(e)}
            return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class Profile(LifecycleModelMixin, models.Model):
    GENDER_CHOICES = (
        ('M', 'MALE'), ('F', 'FEMALE'), ('other', 'OTHER')
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE, related_name='profile')
    email  = models.EmailField(max_length=100)
    first_name  = models.CharField(max_length=100,  blank=True)
    middle_name  = models.CharField(max_length=100,  blank=True)
    last_name  = models.CharField(max_length=100,  blank=True)
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES)
    bio = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return f'{self.first_name} {self.middle_name} {self.last_name}'
    
    @hook(AFTER_UPDATE,when_any=['first_name','last_name','email'], has_changed=True)
    def update_user_detials(self):
        user = CustomUser.objects.filter(id=self.user.id).update(email=self.email, first_name=self.first_name, last_name=self.last_name)

    def __str__(self):
        return f'{self.user.email} profile'
    
    def get_age(self) -> int:
        '''Calculate the user age using the current date and date of birth'''
        dob = self.date_of_birth
        if dob:
            today = now().date()
            age = today.year - dob.year - (
                (today.month, today.day) < (dob.month, dob.day)
            )
            return age
        return dob
    
    def delete(self, *args, **kwargs):
        """
        Deletes the associated user, which will automatically delete this profile
        due to the on_delete=models.CASCADE setting.
        """
        try:
            user = CustomUser.objects.get(id=self.user_id)
            return user.delete()
        except CustomUser.DoesNotExist:
            pass

    class Meta:
        ordering = ['-created_at']
