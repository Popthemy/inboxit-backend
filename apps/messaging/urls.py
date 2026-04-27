from rest_framework.routers import DefaultRouter
from .views import RouteViewSet, MessageViewSet, SendEmailWithApiKeyView, UserUsageView,RouteApiKeyViewSet
from django.urls import path


router = DefaultRouter()
router.register("routes", RouteViewSet, basename="routes")
router.register("route-apikeys", RouteApiKeyViewSet, basename="routes_apikey")
router.register("messages", MessageViewSet, basename="messages")


urlpatterns = [
  path('user-usage/', UserUsageView.as_view(), name='user-usage'),
  path("send-email/", SendEmailWithApiKeyView.as_view(), name="send-email"),

] + router.urls
