from rest_framework import serializers
from .models import APIKey


class ListApiKeySerializer(serializers.ModelSerializer):
    channel = serializers.CharField(source='route.channel', read_only=True)

    class Meta:
        model = APIKey
        fields = ('id', "uid",  'route', 'prefix', 'is_active', "is_revoked","revoked_at", "env_choice",
                  'channel', 'usage_count', "last_used_at", 'created_at')
        read_only_fields = ('prefix', 'is_active', 'channel',"is_revoked","revoked_at",
                            "last_used_at", 'usage_count')

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if self.context.get('request'):
    #         user = self.context['request'].user
    #         self.fields['route'].queryset = user.routes.all()

    def validate(self, attrs):
        route = attrs.get('route')
        if route is None:
            raise serializers.ValidationError(
                'No route selected for this APIKEY')
        return attrs

    def create(self, validated_data):
        route = validated_data['route']
        env_choice = validated_data.get("env_choice","test")

        if route.keys.filter(is_active=True).exists():
            raise serializers.ValidationError(
                'These route still has a valid api key. Use the old Api Key or revoke the old api')

        # user = validated_data['user']
        return APIKey.issue_for(route=route, env_choice=env_choice)
        # return APIKey.issue_for(user=user, route=route)


class ApiKeySerializer(serializers.ModelSerializer):
    # user = serializers.SerializerMethodField()
    route = serializers.SerializerMethodField()

    class Meta:
        model = APIKey
        fields = ('id', "uid", 'key_hash', 'prefix', 'is_active', "env_choice", "is_revoked", 'revoked_at',
                  'route', 'last_used_at', 'usage_count', 'created_at')
        read_only_fields = ('prefix','channel',
                            "last_used_at", 'usage_count')

    # def get_user(self, obj) -> dict:
    #     return {
    #         "id": obj.user.id,
    #         "user": obj.user.email,
    #     }

    def get_route(self, obj) -> dict:
        route = obj.route
        return {
            "id": route.id,
            "user": {
                "id": route.user.id,
                "user": route.user.email,
            },
            "channel": route.channel,
            "recipient_emails": route.recipient_emails,
            "is_active": route.is_active
        }
