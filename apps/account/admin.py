from django.contrib import admin
from .models import CustomUser, VerifyOTP,Profile
# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name')
    search_fields = ('first_name', 'last_name', 'email',)

    class Meta:
        model = CustomUser
        fields = '__all__'


@admin.register(VerifyOTP)
class VerifyOTPAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'otp', 'purpose', 'created_at')
    search_fields = ('email',)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'otp', 'created_at')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'full_name', 'gender','age')
    search_fields = ('first_name','last_name')

    def age(self, instance):
        return instance.get_age()

    class Meta:
        model = Profile
        fields = ('user', 'first_name', 'email', 'middle_name',
                  'last_name', 'gender', 'age', 'bio')
