from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator


class CustomBaseUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        '''create and save user with the given details'''

        if not email:
            raise ValueError('Email is a required field')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            try:
                validate_password(password=password)
            except Exception as e:
                raise ValueError(f'Password : {str(e)}') from e
        else:
            raise ValueError('Password is a required field')

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser must be True')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('is_staff must be True')

        return self.create_user( email=email, password=password, **extra_fields)
