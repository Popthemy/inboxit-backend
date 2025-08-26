from django.contrib import admin
from .models import Message, Route
# Register your models here.


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('channel', 'user')



@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass
