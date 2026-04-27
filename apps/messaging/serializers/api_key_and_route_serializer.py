
import django
from rest_framework import serializers
from django.db import transaction
from apps.key.serializers import ListApiKeySerializer
from ..services.route_service import RouteService
from ..services.notification_service import MessagingNotificationService
from .main_serializers import RouteSerializer


class ApiKeyInputSerializer(serializers.Serializer):
    from apps.key.models import APIKey
    env_choices = serializers.ChoiceField(choices=APIKey.Environment.choices)


class RouteApiKeySerializer(RouteSerializer):
    api_keys = ListApiKeySerializer(many=True, read_only=True, source='keys')
    # api_key = serializers.JSONField(write_only=True, required=False)
    # api_key = ApiKeyInputSerializer(write_only=True, required=False)
    user = serializers.SerializerMethodField(read_only=True)

    class Meta(RouteSerializer.Meta):
        fields = RouteSerializer.Meta.fields + ('api_keys', "user")

    def get_user(self, obj) -> dict:
        return {
            "id": obj.user.id,
            "user": obj.user.email,
        }

    def create(self, validated_data):
        """
        This method creates a route and optionally creates an API key for that route if api_key data is provided in the request.
            - If api_key data is provided, it checks if the route already has an active API key. If it does, it raises a validation error.
            Request body example:
            {
            "channel": "email",
            "recipient_emails": "edupima@gmail.com, pima@gmail.com",
            "label": "quote form",
            "api_keys": {
                "env_choice": "production"
            }
        """
        user = self.context["request"].user
        print("user in route apikey serializer:", user)
        # user = self.context["request"].user
        # print("user in route apikey:",user)
        route, keys = RouteService.create_route(validated_data, user=user)
        MessagingNotificationService.route_created(route)

        route._raw_api_keys = keys
        return route


    def to_representation(self, instance):
        data = super().to_representation(instance)
        keys_list = data.get('api_keys', {})
        keys_map = {}

        # Convert list → object keyed by env
        for key in keys_list:
            env = key.get("env_choice")
            keys_map[env] = key

        # Inject raw keys if present (on create)
        if hasattr(instance, '_raw_api_keys'):
            raw_map = instance._raw_api_keys

            for env, raw in raw_map.items():
                if env in keys_map:
                    keys_map[env]['key'] = raw.get('key')
        data["api_keys"] = keys_map
        return data
