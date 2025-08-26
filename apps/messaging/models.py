from django.db import models
from django.conf import settings
from django.urls import reverse
# Create your models here.

User = settings.AUTH_USER_MODEL


class Route(models.Model):
    '''
    1 route per apikey or different route for different unique api_key
    '''
    
    CHANNEL_EMAIL = "email"
    CHANNEL_CHOICES = [(CHANNEL_EMAIL, "Email")]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="routes")
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    is_active = models.BooleanField(default=True)
    recipient_email = models.EmailField(help_text='this email receives the email ')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)


    def __str__(self):
        return f'{self.channel} - {self.recipient_email}'


class Message(models.Model):

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"


    apikey = models.ForeignKey(
        "key.APIKey", on_delete=models.CASCADE, related_name="messages"
    )

    recipient_email = models.EmailField()
    visitor_email = models.EmailField()  # from contact form
    subject = models.CharField(max_length=255, default="New Contact Message")
    body = models.JSONField()
    accepted_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, default="queued", choices=Status.choices
    )
    error = models.TextField(blank=True)
    preview_link = models.URLField(blank=True, null=True)
    attachments = models.FileField(
        upload_to="messages/attachments/", blank=True, null=True)

    image_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ("-accepted_at",)

    def __str__(self):
        return f"{self.status.upper()} → {self.recipient_email} from {self.visitor_email}"
