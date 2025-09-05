"""
WSGI config for base project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv
from whitenoise import WhiteNoise
from django.core.wsgi import get_wsgi_application
load_dotenv()

settings_module = os.getenv('DJANGO_SETTINGS_MODULE', 'base.settings.development')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()
application = WhiteNoise(application)
