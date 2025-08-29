from .general import *
from dotenv import load_dotenv
from django.conf import settings
load_dotenv()


ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


# email
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = f'{MEDIA_ROOT}/emails'

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587 #465
EMAIL_HOST_USER = os.getenv("EMAIL")
EMAIL_HOST_PASSWORD = os.getenv("PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("EMAIL")
EMAIL_TIMEOUT = 120
