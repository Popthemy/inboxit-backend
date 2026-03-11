from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from .validators import validate_file_size, validate_email_list
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
    recipient_emails = models.TextField(
        help_text='Comma separated emails that receive the message', validators=[validate_email_list])
    # recipient_email = models.EmailField(
    #     help_text='this email receives the message')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at', '-is_active')

    def __str__(self):
        return f'{self.channel} - {self.recipient_emails} ({ "Active" if self.is_active else "Inactive"})'


class Message(models.Model):

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    apikey = models.ForeignKey(
        "key.APIKey", on_delete=models.CASCADE, related_name="messages"
    )

    recipient_emails = models.TextField(
        help_text='Comma separated emails that receive the message', validators=[validate_email_list])
    # recipient_email = models.EmailField()
    visitor_email = models.EmailField()  # from contact form
    subject = models.CharField(max_length=255, default="New Contact Message")
    body = models.JSONField()
    accepted_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, default="queued", choices=Status.choices
    )
    error = models.TextField(blank=True)
    attachments = models.FileField(
        upload_to="messages/attachments/", blank=True, null=True,
        validators=[validate_file_size, FileExtensionValidator(allowed_extensions=('pdf,doc'))])
    image_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ("-accepted_at", '-sent_at')

    def __str__(self):
        return f"{self.status.upper()} → {self.recipient_emails} from {self.visitor_email}"

    def get_absolute_url(self):
        return reverse("messages-detail", kwargs={"pk": self.pk})


class UserUsage(models.Model):
    '''
    Tracks per-user usage irregardless of api-key activeness
    at the end of the day use a cron job to set the total request= total+Today, 
    group when setting 
    '''

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='usage')
    total_requests = models.PositiveIntegerField(default=0)
    requests_today = models.PositiveIntegerField(default=0)
    last_request_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-requests_today', '-total_requests')

    def __str__(self):
        return f'Overall Req:{self.total_requests} - Today Req: {self.requests_today} '
