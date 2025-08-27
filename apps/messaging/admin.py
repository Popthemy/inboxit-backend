from django.contrib import admin
from .models import Message, Route, UserUsage
# Register your models here.


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('channel', 'user')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject','status', 'sent_at')


@admin.register(UserUsage)
class UserUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_requests', 'requests_today')
