import json
from rest_framework import serializers
from .models import Message, Route, UserUsage


class UserUsageSerializer(serializers.ModelSerializer):

    user_details = serializers.SerializerMethodField()

    class Meta:
        model = UserUsage
        fields = ('user_details', 'total_requests', 'requests_today')

    def get_user_details(self, obj) -> dict:
        return {
            'id': obj.user.id,
            'email': obj.user.email
        }


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id", "user", "channel", "is_active",
            "recipient_emails", "created_at"
        )
        read_only_fields = ("id", "created_at", "user")

    def create(self, validated_data):
        user = self.context["request"].user
        return Route.objects.create(user=user, **validated_data)


class ListMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            "id", "visitor_email", "recipient_emails", "subject", "sent_at", "status"
        )
        read_only_fields = fields


class MessageSerializer(serializers.ModelSerializer):
    website = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Message
        fields = (
            "id", "apikey", "visitor_email", "recipient_emails", "subject",
            "body", "accepted_at", "sent_at", "status",
            "error", "attachments", "image_url", "website"
        )
        read_only_fields = [
            "id", "apikey", "recipient_emails", "accepted_at", "sent_at", "status", "error"
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
