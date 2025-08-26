from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework.exceptions import ValidationError


def send_message_email(message):
    '''
    send message using persist message object
    '''

    try:
        from_email = settings.EMAIL_HOST_USER
        to_email = [message.channel.recipient_email]
        subject = f"INBOXIT - NEW MESSAGE FROM YOUR WEBSITE VISITOR({to_email[0].split('@')[0]})"
        print(f'email services: {subject}')

        context = {
            'subject': subject,
            'body': message,
            'preview_url': message.absolute_url or '#',
            'dashboard_url': settings.HOMEPAGE or '#',
            'time': timezone.now(),
        }

        html_content = render_to_string(
            'email\send_message_with_email.html', context)

        email = EmailMultiAlternatives(
            subject, '', from_email, to_email, reply_to=message.vistor_email)
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

    except Exception as e:
        raise ValidationError(f'Mail not sent. {e}')
