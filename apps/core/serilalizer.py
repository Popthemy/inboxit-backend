from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import  Notification


class NotificationListSerializer(serializers.ModelSerializer):
    # content_type = serializers.PrimaryKeyRelatedField(source="content_type", read_only=True)
    class Meta:
        model = Notification
        # fields = ['id', 'type', "content_type",  "title",
        #           'is_read', "object_id", 'created_at']
        fields =  ['id', 'user', 'type', 'is_read',
                  'created_at', 'title', 'message', "object_id"]


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ['id', 'user', 'type', 'is_read', "content_type",
                  'created_at', 'title', 'message', "object_id"]
