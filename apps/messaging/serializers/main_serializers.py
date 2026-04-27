import json
from rest_framework import serializers
from ..models import Message, Route, UserUsage 
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError as DjangoValidationError

class UserUsageSerializer(serializers.ModelSerializer):

    user_details = serializers.SerializerMethodField()

    class Meta:
        model = UserUsage
        fields = ("id","uid", 'user_details', 'total_requests', 'requests_today')

    def get_user_details(self, obj) -> dict:
        return {
            'id': obj.user.id,
            'email': obj.user.email
        }


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id", "uid", "label", "user", "channel", "is_active",
            "recipient_emails", "config",'is_deleted',"deleted_at",  "created_at"
        )
        read_only_fields = ("id", "created_at", "user","is_deleted", "deleted_at")

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        channel = attrs.get('channel') or getattr(instance, "channel", None)

        base_config = dict(getattr(instance, "config", {}) or {})
        incoming_config = attrs.get('config', {})

        config = {**base_config, **incoming_config}

        is_config_updated = 'config' in attrs or 'recipient_emails' in attrs

        # BACKWARD COMPAT
        if 'recipient_emails' in attrs:
            config['recipient_emails'] = attrs.pop('recipient_emails')

        # ✅ ONLY validate if relevant fields are touched
        if channel == 'email' and is_config_updated:
            emails = config.get('recipient_emails')

            if not isinstance(emails, list):
                raise serializers.ValidationError({
                    "config": {
                        "recipient_emails": "Must be a list of emails"
                    }
                })

            if not emails:
                raise serializers.ValidationError({
                    "config": {
                        "recipient_emails": "At least one recipient email is required"
                    }
                })

            validator = EmailValidator()
            for email in emails:
                try:
                    validator(email)
                except DjangoValidationError:
                    raise serializers.ValidationError({
                        "config": {
                            "recipient_emails": f"Invalid email: {email}"
                        }
                    })

        elif channel == 'sms' and is_config_updated:
            if not config.get('phone_number'):
                raise serializers.ValidationError({
                    "config": {
                        "phone_number": "Required for sms channel"
                    }
                })

        attrs['config'] = config
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        return Route.objects.create(user=user, **validated_data)


class ListMessageSerializer(serializers.ModelSerializer):
    apikey = serializers.StringRelatedField()

    class Meta:
        model = Message
        fields = (
            "id", "uid", "apikey", "visitor_email", "recipient_emails", "subject", "sent_at", "status"
        )
        read_only_fields = fields


class MessageSerializer(serializers.ModelSerializer):
    website = serializers.CharField(required=False, allow_blank=True)
    apikey = serializers.StringRelatedField()
    class Meta:
        model = Message
        fields = (
            "id", "uid", "apikey", "visitor_email", "recipient_emails", "subject",
            "body", "accepted_at", "sent_at", "status",
            "error", "attachments", "image_url", "website"
        )
        read_only_fields = [
            "id", "uid", "apikey", "recipient_emails", "accepted_at", "sent_at", "status", "error"
        ]

    def to_internal_value(self, data):
        '''convert body to json'''
        body = data.get('body')

        if isinstance(body, str):
            data['body'] = {'text': body}
        return super().to_internal_value(data)

    def validate(self, attrs):
        website = attrs.get("website", "")

        if website:
            raise serializers.ValidationError("Spam detected.")
        return super().validate(attrs)

    def create(self, validated_data):
        return Message.objects.create(**validated_data)
