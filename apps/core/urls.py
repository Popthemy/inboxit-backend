from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()

# 1. Notifications Endpoint
router.register(r'notifications', views.NotificationListView,
                basename='notification')


urlpatterns = [
    path("", include(router.urls)),
]
