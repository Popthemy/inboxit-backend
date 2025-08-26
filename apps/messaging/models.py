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
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages")
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="messages")
    payload = models.JSONField()
    visitor_email = models.EmailField()
    accepted_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20, default="queued")  # queued/sent/failed
    error = models.TextField(blank=True)

    class Meta:
        ordering = ('-sent_at',)

    def __str__(self):
        return f' {self.status}: {self.route.recipient_email} - {self.visitor_email}'

    def get_absolute_url(self):
        return reverse("model_detail", kwargs={"pk": self.pk})
