from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class NotificationType(models.TextChoices):
    ROUTE_CREATED = "route_created", "Route Created"
    ROUTE_UPDATED = "route_updated", "Route Updated"
    ROUTE_DISABLED = "route_disabled", "Route Disabled"
    ROUTE_ENABLED = "route_enabled", "Route Enabled"

    API_KEY_CREATED = "api_key_created", "API Key Created"
    API_KEY_REGENERATED = "api_key_regenerated", "API Key Regenerated"
    API_KEY_REVOKED = "api_key_revoked", "API Key Revoked"

    MESSAGE_SENT = "message_sent", "Message Sent"
    MESSAGE_FAILED = "message_failed", "Message Failed"

    VERIFICATION_PENDING = "verification_pending", "Verification Pending"
    VERIFICATION_APPROVED = "verification_approved", "Verification Approved"

    USAGE_THRESHOLD_WARNING = "usage_threshold_warning", "Usage Threshold Warning"
    ACCOUNT_SECURITY_ALERT = "account_security_alert", "Account Security Alert"
    TEAM_INVITE = "team_invite", "Team Invite"


class Notification(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    type = models.CharField(max_length=50, choices=NotificationType.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.CharField(max_length=255, blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["created_at"]),
        ]

    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=["is_read"])

    def to_json(self):
        return {
            "id": str(self.id) if hasattr(self, 'id') else None,
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat(),
            # You can add the object_id so the frontend knows where to redirect
            "target_id": str(self.object_id)
        }

    def __str__(self):
        return f"{self.user} - {self.type}"
