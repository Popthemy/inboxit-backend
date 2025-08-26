from rest_framework.routers import DefaultRouter
from .views import RouteViewSet, MessageViewSet, SendEmailWithApiKeyView
from django.urls import path


router = DefaultRouter()
router.register("routes", RouteViewSet, basename="routes")
router.register("messages", MessageViewSet, basename="messages")


urlpatterns = [
  path("send-email/", SendEmailWithApiKeyView.as_view(), name="send-email"),
] + router.urls
