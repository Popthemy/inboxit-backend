from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Profile

User = get_user_model()


class OTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)


class PasswordResetSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs['new_password']
        if password != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")

        try:
            validate_password(password=password)
        except Exception as e:
            raise serializers.ValidationError("Passwords f{e}") from e

        return attrs


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(max_length=30, write_only=True)
    confirm_password = serializers.CharField(max_length=30, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name',
                  'agree_to_privacy_policy', 'password', 'confirm_password',)

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError(
                "Password and Confirm_password doesn't match")

        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError(str(e)) from e

        attrs.pop('confirm_password', None)
        return attrs

    def create(self, validated_data):
        ''''Turn is_active to false, activation as means of validating user email'''
        user = User.objects.create_user(is_active=False, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=30, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = User.objects.filter(email=email).first()
            if user:
                if user.check_password(password):
                    return attrs
            raise serializers.ValidationError('Invalid Email or password!')
        raise serializers.ValidationError('Email or Password are required!')


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='user_id',read_only=True)
    age = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = ('id', 'email', 'first_name', 'middle_name', 'last_name', 'date_of_birth', 'age',
                  'gender', 'bio', 'phone_number', 'created_at', 'updated_at')
    
    def get_age(self, instance) -> int:
        return instance.get_age()

    def update(self, instance, validated_data):
        validated_data['user'] = self.context['user']
        return super().update(instance, validated_data)
