from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .utils import hash_key
from .models import APIKey


class ApiKeyAuthentication(BaseAuthentication):
    """
    Accepts:
      - X-Api-Key: <raw>  (preferred)
      - ?apikey=<raw>     (fallback for static forms)
    Returns (user, api_key_obj) if valid.
    """

    def authenticate(self, request):
        raw = request.headers.get(
            "X-Api-Key") or request.query_params.get("apikey")
        if not raw:
            return None

        key_hash = hash_key(raw)
        try:
            obj = APIKey.objects.select_related("user").get(
                key_hash=key_hash, is_active=True)
            return (obj.user, obj)

        except APIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid or revoked API key")


class CookieJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'apps.key.authentication.ApiKeyAuthentication'
    name = 'ApiKeyAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'str',
            'in': 'query or header',
            'name': 'api_key'
        }
