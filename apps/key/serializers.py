from rest_framework import serializers
from .models import APIKey
from apps.messaging.models import Route


class ListApiKeySerializer(serializers.ModelSerializer):
    channel = serializers.CharField(source='route.channel', read_only=True)

    class Meta:
        model = APIKey
        fields = ('id', 'route', 'prefix', 'is_active', 'channel', 'usage_count')
        read_only_fields = ('prefix', 'is_active', 'channel', 'usage_count')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get('request'):
            user = self.context['request'].user
            self.fields['route'].queryset = user.routes.all()

    def validate(self, attrs):
        route = attrs.get('route')
        if route is None:
            raise serializers.ValidationError(
                'No route selected for this APIKEY')
        return attrs

    def create(self, validated_data):
        route = validated_data['route']

        if route.keys.filter(is_active=True).exists():
            raise serializers.ValidationError(
                'These route still has a valid api key. Use the old Api Key or revoke the old api')

        user = validated_data['user']
        return APIKey.issue_for(user=user, route=route)


class ApiKeySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    route = serializers.SerializerMethodField()

    class Meta:
        model = APIKey
        fields = ('id', 'user', 'key_hash', 'prefix', 'is_active', 'revoked_at',
                  'route', 'last_used_at', 'usage_count', 'created_at')

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "user": obj.user.email,
        }

    def get_route(self, obj):
        return {
            "id": obj.route.id,
            "channel": obj.route.channel,
            "recipient_email": obj.route.recipient_email,
            "is_active": obj.route.is_active
        }
