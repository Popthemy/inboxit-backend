import hmac, hashlib
from django.conf import settings


def hash_key(plaintext: str) -> str:
    # HMAC-SHA256 with SECRET_KEY
    return hmac.new(
        key=settings.SECRET_KEY.encode("utf-8"),
        msg=plaintext.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()
