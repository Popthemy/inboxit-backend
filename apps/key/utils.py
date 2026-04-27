import hmac, hashlib
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


def hash_key(plaintext: str) -> str:
    # HMAC-SHA256 with SECRET_KEY
    return hmac.new(
        key=settings.SECRET_KEY.encode("utf-8"),
        msg=plaintext.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()


def check_route_regeneration_limit(route, user):
    '''
    restrict user from regenerating a route more than 5/day
    '''
    from .models import KeyRegenerationLog
    since = timezone.now() - timedelta(days=1)

    count = KeyRegenerationLog.objects.filter(
        route=route,
        user=user,
        created_at__gte=since
    ).count()

    if count >= 5:
        raise ValueError(
            "You can only regenerate API keys 5 times per route per 24 hours."
        )
