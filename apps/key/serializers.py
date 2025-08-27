from rest_framework import serializers
from .models import APIKey
from apps.messaging.models import Route


class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ('id', 'user', 'key_hash', 'prefix', 'is_active', 'revoked_at',
                  'route', 'last_used_at', 'usage_count', 'created_at')


class CreateApiKeySerializer(serializers.ModelSerializer):

    class Meta:
        model = APIKey
        fields = ('route',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context['request'].user
        self.fields['route'].queryset = user.routes.all()


    def validate(self, attrs):
        route = attrs.get('route')
        if route is None:
            raise serializers.ValidationError('No route selected for this APIKEY')
        return attrs

    def create(self, validated_data):
        route = validated_data['route']
        print(route.keys.filter(is_active=True))
        if route.keys.filter(is_active=True).exists():
            
            raise serializers.ValidationError('These route still has a valid api key. Use the old Api Key or revoke the old api')
        user = validated_data['user']
        return APIKey.issue_for(user=user, route=route)



