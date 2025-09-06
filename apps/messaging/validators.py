from django.core.exceptions import ValidationError

def validate_file_size(value):
    limit = 5 * 1024 * 1024  # 5 MB limit
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 5 MB.')