from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework.exceptions import ValidationError


def send_message_email(message):
    '''
    send message using persist message object
    setup cron job to resend failed message
    '''
    try:
        from_email = settings.EMAIL_HOST_USER
        to_email = [message.recipient_email]
        subject = message.subject
        visitor_email = message.visitor_email
        now = timezone.now()
        print(f'email services: {subject}')

        text_content = f"{message.body}\n\nReply to: {visitor_email}"

        context = {
            'subject': subject,
            'body': message.body.get(message) if isinstance(message.body, dict) else message.body,
            'image_url':message.image_url,
            'preview_link': message.preview_url or '#',

            'dashboard_link':  f"{settings.HOMEPAGE}dashboard" if settings.homepage else '#',
            'time': now,
        }

        html_content = render_to_string(
            'email/send_message_with_email.html', context)

        email = EmailMultiAlternatives(
            subject, text_content, from_email, to_email, reply_to=[visitor_email])
        email.attach_alternative(html_content, "text/html")

        if message.attachments:
            email.attach_file(message.attachments.path)

        email.send(fail_silently=False)
        message.status = "sent"
        message.sent_at = now()
        message.save()
    except Exception as e:
        message.status = "failed"
        message.error = str(e)
        message.save()
        raise ValidationError(f'email not sent: {e}') from e
