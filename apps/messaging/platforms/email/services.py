from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import F
from rest_framework.exceptions import ValidationError
from apps.messaging.models import UserUsage


def safe_email_header(value: str) -> str:
    return value.replace('\r', '').replace('\n', '')


def format_body(body):
    if isinstance(body, dict):
        # turn dict into HTML definition list
        rows = "".join(
            f"<tr><td><strong>{key}</strong></td><td>{value}</td></tr>"
            for key, value in body.items()
        )
        return f"<table style='border-collapse: collapse; width: 100%;'>" \
               f"<tbody>{rows}</tbody></table>"
    return f"<p>{body}</p>"


def send_message_email(message):
    '''
    send message using persist message object
    setup cron job to resend failed message
    '''
    try:
        from_email = settings.EMAIL_HOST_USER
        to_email = to_email = [
            email.strip()
            for email in message.recipient_emails.split(",")
            if email.strip()
        ]
        subject = safe_email_header(message.subject)
        visitor_email = message.visitor_email
        now = timezone.now()
        print(
            f"[Email] Sending to: {to_email}, from: {from_email}, reply to: {visitor_email} subject: {subject}")

        text_content = f"{message.body}\n\nReply to: {visitor_email}"

        context = {
            'subject': subject,
            'body_html': format_body(message.body),
            'image_url': message.image_url,
            # f"{settings.FRONTEND_URL}{message.get_absolute_url()}{subject.replace(' ', '-')}" if settings.FRONTEND_URL else '#',
            'preview_link': "#",
            # f"{settings.FRONTEND_URL}dashboard" if settings.FRONTEND_URL else '#',
            'dashboard_link':  '#',
            'time': now,
        }

        html_content = render_to_string(
            'email/email-template.html', context)

        email = EmailMultiAlternatives(
            subject, text_content, from_email, to_email, reply_to=[visitor_email])
        email.attach_alternative(html_content, "text/html")

        if message.attachments:
            email.attach_file(message.attachments.path)

        email.send(fail_silently=False)
        message.status = "sent"
        message.sent_at = now
        message.save()
    except Exception as e:
        message.status = "failed"
        message.error = str(e)
        message.save()
        raise ValidationError(f'Failed to send message: {e}') from e


def increment_user_usage(apikey_obj):
    '''
    Increment the user usage for after each email
    '''

    now = timezone.now()

    usage, _ = UserUsage.objects.select_for_update().get_or_create(user=apikey_obj.user)

    if usage.last_request_at is None or usage.last_request_at.date() != now.date():
        usage.requests_today = 0
    else:
        usage.requests_today = F('requests_today') + \
            1  # Use F() only when no reset

    usage.requests_today = F('requests_today') + 1
    usage.last_request_at = now

    usage.save(update_fields=['total_requests',
               'requests_today', 'last_request_at'])

    # Update API key usage safely
    apikey_obj.usage_count = F('usage_count') + \
        1 if apikey_obj.usage_count else 1
    apikey_obj.last_used_at = now
    apikey_obj.save(update_fields=["usage_count", "last_used_at"])
