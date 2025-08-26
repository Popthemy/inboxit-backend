from rest_framework import serializers
from .models import Message, Route


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id", "user", "channel", "is_active",
            "recipient_email", "created_at"
        )
        read_only_fields = ("id", "created_at", "user")

    def create(self, validated_data):
        user = self.context["request"].user
        return Route.objects.create(user=user, **validated_data)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            "id", "apikey", "visitor_email","recipient_email", "subject",
            "body", "accepted_at", "sent_at", "status",
            "error", "attachments", "image_url"
        )
        read_only_fields = [
            "id", "apikey", "recipient_email", "accepted_at", "sent_at", "status", "error"
        ]

    def create(self, validated_data):
        return Message.objects.create(**validated_data)
