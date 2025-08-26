from django.contrib import admin
from .models import APIKey, UserUsage


# Register your models here.
@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'prefix', 'is_active', 'route',
                    'usage_count', 'revoked_at')
    list_editable = ('is_active', )
    list_filter = ('is_active', )
    search_fields = ('default_route',)


@admin.register(UserUsage)
class UserUsageAdmin(admin.ModelAdmin):
    list_display = ('total_requests', 'requests_today')
