from django.urls import path
from . import views


urlpatterns = [
    path('apikeys/',view=views.ApiKeyView.as_view(), name='get_create_apikeys'),
    path('apikeys/<int:pk>/',view=views.RevokeApiKeyView.as_view(), name='revoke_apikeys'),
]
