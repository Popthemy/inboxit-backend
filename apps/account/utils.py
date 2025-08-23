
import threading
import hashlib
import random
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .models import VerifyOTP

User = get_user_model()

OTP_EMAIL_EXPIRY_TIME = settings.OTP_EMAIL_EXPIRY_TIME
OTP_PASSWORD_EXPIRY_TIME = settings.OTP_PASSWORD_EXPIRY_TIME


def get_otp_expiry_time(purpose: str):
    """Get purpose-specific expiry time"""
    return {
        'email': settings.OTP_EMAIL_EXPIRY_TIME,
        'password': settings.OTP_PASSWORD_EXPIRY_TIME,
    }.get(purpose, 10)


def send_email_with_url(email: str, subject: str, otp_code: str, purpose: str, url_name: str, template: str, *args):
    '''
    subject = subject of the mail
    email = recipient to send mail to
    otp_code: raw otp
    purpose = the type of the otp
    url_name: URL name for verification endpoint
    template e.g 'account/verification_otp.html'
    '''

    recipient = [email]

    try:
        # verify_url = reverse(url_name)
        # full_url = f"{FRONTEND_URL}{verify_url}?email={email}"
        full_url = f"{url_name}?email={email}"

        context = {'email': email, 'purpose': purpose,
                   'otp_code': otp_code, 'otp_expiry_time': get_otp_expiry_time(purpose),
                   'verify_otp_url': full_url
                   }

        email_thread = EmailThread(subject, recipient, template, context)
        email_thread.start()
    except Exception as e:
        raise ValidationError(str(e)) from e


class OTPService:
    """managing OTP"""

    @staticmethod
    def _generate_otp() -> str:
        """Generate 6-digit OTP"""
        return str(random.randint(100000, 999999))

    @staticmethod
    def _hash_otp(raw_otp: str) -> str:
        """ Hash OTP using SHA-256"""
        return hashlib.sha256(raw_otp.encode()).hexdigest()

    @staticmethod
    def _store_otp(email: str, hashed_otp: str, purpose: str) -> None:
        """ Persist OTP record"""
        VerifyOTP.objects.create(
            email=email,
            otp=hashed_otp,
            purpose=purpose
        )

    @staticmethod
    def _expire_old_otps(email: str, purpose: str) -> int:
        """Cleanup existing OTPs (returns deleted count)"""
        return VerifyOTP.objects.filter(
            email=email,
            purpose=purpose
        ).delete()[0]

    @classmethod
    def generate_and_store_otp(cls, email: str, purpose: str) -> str:
        """
        Generate the otp, delete if user has a previous otp for that purpose,
        stored the hashed otp with the purpose,
        return the raw otp to be sent in the mail
        """
        raw_otp = cls._generate_otp()
        cls._expire_old_otps(email, purpose)
        cls._store_otp(email, cls._hash_otp(raw_otp), purpose)
        return raw_otp

    @staticmethod
    def verify_and_delete_otp(email: str, raw_otp: str, purpose: str) -> bool:
        """check if the otp for that purpose exist"""
        try:
            record = VerifyOTP.objects.get(
                email=email, purpose=purpose, otp=hashlib.sha256(
                    raw_otp.encode()).hexdigest()
            )
            expiry_time = record.created_at + \
                timezone.timedelta(minutes=get_otp_expiry_time(purpose))
            if timezone.now() > expiry_time:
                record.delete()
                return False
            record.delete()
            return True
        except VerifyOTP.DoesNotExist:
            return False


class EmailThread(threading.Thread):
    def __init__(self, subject: str, recipient_list: list, template: str, context: dict):
        self.subject = subject
        self.template = template
        self.recipient_list = recipient_list
        self.context = context
        super().__init__()

    def run(self):
        try:
            email = EmailMessage(
                subject=self.subject,
                body=render_to_string(self.template, context=self.context),
                from_email=settings.EMAIL_HOST_USER,
                to=self.recipient_list,
            )
            email.content_subtype = 'html'
            email.send(fail_silently=False)
        except Exception as e:
            raise ValidationError(f"Email not sent: {e}") from e



def send_login_email(user, order, items, url):
    try:

        subject = f"Blakkart - {action} Confirmation"
        from_email = settings.EMAIL_HOST_USER
        to_email = [user.email]

        context = {
            'user': user,
            'order': order,
            'now':  timezone.now(),
            'order_url':  url  # f"{FRONTEND_URL}/{order.id}/",

            
        }

        context = {
            'user': user,
            'login_time': timezone.now(),
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
            'shop_url': request.build_absolute_uri(reverse('shop')),
            'profile_url': request.build_absolute_uri(reverse('profile')),
            'deals_url': request.build_absolute_uri(reverse('deals')),
            'security_url': request.build_absolute_uri(reverse('security')),
            'help_center_url': 'https://blakkart.com/help',
            'privacy_policy_url': 'https://blakkart.com/privacy',
            'unsubscribe_url': request.build_absolute_uri(reverse('unsubscribe')),
        }

        html_content = render_to_string(
            'emails/order_confirmation.html', context)

        email = EmailMultiAlternatives(subject, '', from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
    except Exception as e:
        raise ValidationError(f'Order Confirmation mail not sent. {e}')
