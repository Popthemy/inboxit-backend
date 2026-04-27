from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from apps.core.models import Notification
import logging

logger = logging.getLogger(__name__)


class NotificationService:

    @staticmethod
    def _format_payload(notification: Notification) -> dict:
        payload = {
            "id": str(notification.id),
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat() if notification.created_at else None,
            "target_id": str(notification.object_id) if notification.object_id else None,
            "target_type": notification.content_type.model if notification.content_type else None,
        }
        logger.debug(
            f"Formatted notification payload for {notification.id}: {payload}")
        return payload

    @staticmethod
    def _push_to_websocket(user_id, notification: Notification):
        channel_layer = get_channel_layer()
        if channel_layer is None:
            logger.error(
                f"Channel layer is not configured. Cannot push notification {notification.id} to user {user_id}")
            raise RuntimeError("Channel layer is not configured")

        payload = NotificationService._format_payload(notification)
        group_name = f"notify_{str(user_id)}"

        try:
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send_notification",
                    "content": payload,
                }
            )
            logger.info(
                f"Successfully pushed notification {notification.id} ({notification.type}) to group {group_name}")
        except Exception as exc:
            logger.error(
                f"Failed to push notification {notification.id} to group {group_name}: {str(exc)}", exc_info=True)
            raise

    @staticmethod
    def _safe_push(user_id, notification: Notification):
        try:
            NotificationService._push_to_websocket(user_id, notification)
        except Exception as exc:
            logger.warning(
                f"WebSocket push failed (non-blocking) for user {user_id}, notification {notification.id}: {str(exc)}")

    @staticmethod
    def create(user, notification_type, title, message, content_object=None):
        logger.info(
            f"Creating notification for user {user.id}: "
            f"type={notification_type}, title={title}"
        )

        notification = Notification.objects.create(
            user=user,
            type=notification_type,
            title=title,
            message=message,
            content_object=content_object,
        )
        logger.info(f"Notification {notification.id} saved to database")

        transaction.on_commit(
            lambda: NotificationService._safe_push(user.id, notification))
        logger.debug(
            f"Scheduled WebSocket push for notification {notification.id} on transaction commit")

        return notification

    @staticmethod
    def bulk_create(data_list):
        logger.info(f"Bulk creating {len(data_list)} notifications")

        for data in data_list:
            data.pop('created_at', None)

        notifications = [Notification(**data) for data in data_list]
        created_objs = Notification.objects.bulk_create(notifications)

        logger.info(
            f"Bulk created {len(created_objs)} notifications: {[str(n.id) for n in created_objs]}")

        transaction.on_commit(
            lambda: [
                NotificationService._safe_push(obj.user.id, obj)
                for obj in created_objs
            ]
        )
        logger.debug(
            f"Scheduled WebSocket pushes for {len(created_objs)} notifications on transaction commit")

        return created_objs

    @staticmethod
    def notify(user, notification_type, title, message, content_object=None):
        return NotificationService.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            content_object=content_object,
        )
