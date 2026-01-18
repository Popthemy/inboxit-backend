from drf_spectacular.extensions import OpenApiAuthenticationExtension
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import CSRFCheck, get_authorization_header

SAFE_METHODS = ('GET', "HEADS", "OPTIONS")


class CookieJWTAuthentication(JWTAuthentication):

    def enforce_csrf(self, request):
        """Enforce CSRF validation for unsafe methods"""
        def dummy_get_response(request):
            return None
        check = CSRFCheck(dummy_get_response)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise AuthenticationFailed('CSRF Failed: %s' % reason)

    def authenticate(self, request):
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])

        if raw_token:
            validated = self.get_validated_token(raw_token)
            if request.method not in SAFE_METHODS:
                self.enforce_csrf(request)
            return self.get_user(validated), validated

        # fallback: Authorization: Bearer <token>
        auth = get_authorization_header(request).split()
        # e.g. ('Bearer',)
        auth_header_types = settings.SIMPLE_JWT['AUTH_HEADER_TYPES']
        if (auth
            and auth[0].decode().lower() in [t.lower() for t in auth_header_types]
                and len(auth) == 2):
            validated = self.get_validated_token(auth[1].decode())
            return self.get_user(validated), validated
        return None



class CookieJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'apps.account.custom_auth.CookieJWTAuthentication'
    name = 'cookieJWTAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'access_token'
        }
