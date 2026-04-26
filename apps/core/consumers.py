import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user", AnonymousUser())

        if self.user.is_anonymous:
            self.group_name = "notify_test_group"
            logger.warning(
                f"Anonymous user attempted WebSocket connection on {self.group_name}")
        else:
            self.group_name = f"notify_{str(self.user.id)}"
            logger.info(
                f"User {self.user.id} ({self.user.email if hasattr(self.user, 'email') else 'unknown'}) connected to {self.group_name}")

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.debug(
            f"WebSocket connection accepted and group added for {self.group_name}")

    async def disconnect(self, close_code):
        logger.info(
            f"User {self.user} disconnected from {self.group_name} with close code {close_code}")
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.debug(f"User removed from group {self.group_name}")

    async def send_notification(self, event):
        notification_data = event.get("content", {})
        logger.info(
            f"Sending notification to {self.group_name}: "
            f"id={notification_data.get('id')}, "
            f"type={notification_data.get('type')}, "
            f"title={notification_data.get('title')}"
        )

        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': notification_data,
        }))
        logger.debug(
            f"Notification sent successfully to WebSocket for {self.group_name}")
