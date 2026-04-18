import secrets
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from .utils import hash_key

class APIKey(models.Model):

    class Environment(models.TextChoices):
        TEST = "test", "Test"
        LIVE = "live", "Live"

    uid = models.UUIDField(default=uuid.uuid4, editable=False, null=True)

    env_choice = models.CharField(
        max_length=10, choices=Environment.choices, default=Environment.TEST)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='api_keys')
    key_hash = models.CharField(max_length=64, unique=True)
    prefix = models.CharField(max_length=14, db_index=True)
    is_active = models.BooleanField(default=True)
    is_revoked = models.BooleanField(default=False)
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
    def issue_for(route, env_choice):
        env_choice = env_choice or APIKey.Environment.TEST
        raw = f"ii_{env_choice}_{secrets.token_urlsafe(32)}"
        key_hash = hash_key(raw)
        prefix = f"ii_{env_choice}_{raw[-6:]}"
        obj = APIKey.objects.create(
            key_hash=key_hash, prefix=prefix, route=route, env_choice=env_choice
        )
        return obj, raw

    def revoke(self):
        """Revoke the API key by marking it as inactive and setting the revoked_at timestamp."""
        self.is_active = False
        self.is_revoked =True
        self.revoked_at = timezone.now()
        self.save(update_fields=["is_active", "revoked_at", "is_revoked",])

    def regenerate(self):
        """
        Revoke the current key and issue a new one with the same route and user.
        """
        self.revoke()
        new_key, raw = APIKey.issue_for(route=self.route, env_choice=self.env_choice)
        return new_key, raw


class KeyRegenerationLog(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    route = models.ForeignKey("messaging.Route", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.route.label}"

