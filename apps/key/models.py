import secrets
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from .utils import hash_key


class APIKey(models.Model):

    class Enviroment(models.TextChoices):
        TEST = "test", "Test"
        LIVE = "live", "Live"

    uid = models.UUIDField(default=uuid.uuid4, editable=False, null=True)

    env_choices = models.CharField(
        max_length=10, choices=Enviroment.choices, default=Enviroment.TEST)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='api_keys')
    key_hash = models.CharField(max_length=64, unique=True)
    prefix = models.CharField(max_length=12, db_index=True)
    is_active = models.BooleanField(default=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    route = models.ForeignKey(
        "messaging.Route", on_delete=models.CASCADE, related_name="keys"
    )
    last_used_at = models.DateTimeField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-is_active','-created_at', "-last_used_at" )

    def __str__(self):
        return f'{self.prefix}'

    @staticmethod
    def issue_for(route, env_choices):
        env_choices = env_choices or APIKey.Enviroment.TEST
        raw = f"ii_{env_choices}_{secrets.token_urlsafe(32)}"
        key_hash = hash_key(raw)
        prefix = f"ii_{env_choices}_{raw[-6:]}"
        obj = APIKey.objects.create(
            key_hash=key_hash, prefix=prefix, route=route, env_choices=env_choices
        )
        return obj, raw

    def revoke(self):
        """Revoke the API key by marking it as inactive and setting the revoked_at timestamp."""
        self.is_active = False
        self.revoked_at = timezone.now()
        self.save(update_fields=["is_active", "revoked_at"])

    def regenerate(self):
        """
        Revoke the current key and issue a new one with the same route and user.
        """
        self.revoke()
        new_key, raw = self.issue_for(route=self.route)
        return new_key, raw
