from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('user-usage' ,viewset=views.UserUsageViewSet, basename='user-usage')

urlpatterns = [
    path('apikeys/',view=views.ApiKeyView.as_view(), name='get_create_apikeys'),
    path('apikeys/<int:pk>/',view=views.RevokeApiKeyView.as_view(), name='revoke_apikeys'),
    path('', include(router.urls)),
]
