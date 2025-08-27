import secrets
from django.db import models
from django.conf import settings
from django.utils import timezone
from .utils import hash_key


class APIKey(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='api_keys')
    key_hash = models.CharField(max_length=64,unique=True)
    prefix = models.CharField(max_length=12, db_index=True)
    is_active = models.BooleanField(default=True)
    revoked_at = models.DateTimeField(null=True,blank=True)
    route = models.ForeignKey(
        "messaging.Route", null=True, blank=True, on_delete=models.SET_NULL, related_name="keys"
    )
    last_used_at = models.DateTimeField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField( auto_now_add=True)

    class Meta:
        # constraints = (models.UniqueConstraint(fields=('default_route','is_active'),name='unique_api_key'),)
        ordering = ('-created_at','-is_active')

    def __str__(self):
        return f'{self.prefix}'

    @staticmethod
    def issue_for(user, route=None):
        raw = secrets.token_urlsafe(32)
        key_hash = hash_key(raw)
        prefix = raw[:8]
        obj = APIKey.objects.create(
            user=user, key_hash=key_hash, prefix=prefix, route=route
        )
        return obj, raw

    def revoke(self):
        self.is_active = False
        self.revoked_at = timezone.now()
        self.save(update_fields=["is_active", "revoked_at"])


