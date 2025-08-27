from django.contrib import admin
from .models import APIKey


# Register your models here.
@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'prefix', 'is_active', 'route',
                    'usage_count', 'revoked_at')
    list_editable = ('is_active', )
    list_filter = ('is_active', )
    search_fields = ('default_route',)

