
import django
from rest_framework import serializers
from apps.key.serializers import ListApiKeySerializer
from apps.key.models import APIKey
from django.db import transaction
from .main_serializers import RouteSerializer

class ApiKeyInputSerializer(serializers.Serializer):
    env_choices = serializers.ChoiceField(choices=APIKey.Enviroment.choices)


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
                "env_choices": "production"
            }
        """

        with transaction.atomic():
            route = super().create(validated_data)

            # if api_key_data:
            # existing_keys = route.keys.filter(is_active=True)
            # existing_envs = set(
            #     existing_keys.values_list('env_choices', flat=True))

            # if "test" in existing_envs or "live" in existing_envs:
            #     raise serializers.ValidationError(
            #         'These route still has a valid api key. Use the old Api Key or revoke the old api')

                # Create TEST key
            test_key, test_raw = APIKey.issue_for(
                route=route,
                env_choices="test",
            )

            # Create LIVE key
            live_key, live_raw = APIKey.issue_for(
                route=route,
                env_choices="live",
            )

            route._raw_api_keys = {
                "test": {
                    "id": test_key.id,
                    "key": test_raw,
                },
                "live": {
                    "id": live_key.id,
                    "key": live_raw,
                }
            }
        return route

    def to_representation(self, instance):
        data = super().to_representation(instance)
        keys_list = data.get('api_keys', [])
        keys_map  = {}
        
        # Convert list → object keyed by env
        for key in keys_list:
            env = key.get("env_choices")
            keys_map[env] = key

        # Inject raw keys if present (on create)
        if hasattr(instance, '_raw_api_keys'):
            raw_map = instance._raw_api_keys

            for env,raw in raw_map.items():
                if env in keys_map:
                    keys_map[env]['key'] = raw.get('key')
        data["api_keys"] = keys_map
        return data
