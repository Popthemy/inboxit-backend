"""
URL configuration for base project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

admin.site.site_title = 'INBOXIT'
admin.site.site_header = 'Welcome to INBOXIT Admin site'
admin.site.index_title = 'Site admin'


first_version = [
    path('', include('apps.messaging.urls')),
    path('', include('apps.key.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.account.urls')),

    path('ap1/v1/',include(first_version)),

    # drf spectacular for documentation
    path('api/doc/', SpectacularAPIView.as_view(), name='schema'),
    path('redoc/', SpectacularRedocView.as_view(), name='redoc'),
    path('', SpectacularSwaggerView.as_view(
        url_name='schema'), name='swagger-ui'),
] 
 
if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns += debug_toolbar_urls()
