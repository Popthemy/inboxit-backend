from django.urls import path
from . import views

# ii_test_gCZd_5HccqV4HiOs5JWk64GRymvmCBtNyYVGipbN59c
urlpatterns = [
    path('apikeys/',view=views.ApiKeyView.as_view(), name='get_create_apikeys'),
    path('apikeys/<int:pk>/',view=views.RevokeApiKeyView.as_view(), name='revoke_apikeys'),
    path('apikeys/<int:pk>/regenerate/', view=views.RegenerateApiKeyView.as_view(),name="regenerate_apikeys"),
]
