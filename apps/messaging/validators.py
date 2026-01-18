from django.core.exceptions import ValidationError


def validate_file_size(value):
    limit = 5 * 1024 * 1024  # 5 MB limit
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 5 MB.')


def validate_email_list(value):
    emails = [email.strip() for email in value.split(',')]
    for email in emails:
        if '@' not in email or '.' not in email:
            raise ValidationError(f'Invalid email address: {email}')
