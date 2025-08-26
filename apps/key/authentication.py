
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from .utils import hash_key
from .models import APIKey, UserUsage


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
        except APIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid or revoked API key")

        usage, _ = UserUsage.objects.get_or_create(user=obj.user)
        usage.total_requests += 1
        usage.requests_today += 1
        usage.save(update_fields=['total_requests', 'requests_today'])

        obj.usage_count = (obj.usage_count or 0) + 1
        obj.last_used_at = timezone.now()
        obj.save(update_fields=["usage_count", "last_used_at"])

        return (obj.user, obj)
