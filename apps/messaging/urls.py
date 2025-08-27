from rest_framework.routers import DefaultRouter
from .views import RouteViewSet, MessageViewSet, SendEmailWithApiKeyView,UserUsageViewSet
from django.urls import path


router = DefaultRouter()
router.register("routes", RouteViewSet, basename="routes")
router.register("messages", MessageViewSet, basename="messages")
router.register('user-usage', UserUsageViewSet, basename='user-usage')


urlpatterns = [
  path("send-email/", SendEmailWithApiKeyView.as_view(), name="send-email"),

] + router.urls
