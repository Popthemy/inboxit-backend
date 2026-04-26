from apps.core.services.notification_service import NotificationService
from apps.core.models import NotificationType
import logging

logger = logging.getLogger(__name__)


class MessagingNotificationService:
    @staticmethod
    def route_created(route):
        user = route.user
        title = "Delivery route created"
        message = (
            f"Your new delivery route '{route.label}' was created with channel "
            f"'{route.channel}'."
        )
        logger.info(
            f"Route {route.id} created for user {user.id} "
            f"(label: {route.label}, channel: {route.channel})"
        )
        return NotificationService.create(
            user=user,
            notification_type=NotificationType.ROUTE_CREATED,
            title=title,
            message=message,
            content_object=route,
        )

    @staticmethod
    def route_updated(route):
        user = route.user
        title = "Delivery route updated"
        message = (
            f"Your delivery route '{route.label}' was updated. "
            f"Please verify the latest settings."
        )
        logger.info(
            f"Route {route.id} updated for user {user.id} (label: {route.label})"
        )
        return NotificationService.create(
            user=user,
            notification_type=NotificationType.ROUTE_UPDATED,
            title=title,
            message=message,
            content_object=route,
        )

    @staticmethod
    def message_sent(message):
        route = getattr(message, 'apikey', None).route if getattr(
            message, 'apikey', None) else None
        user = route.user if route is not None else None
        if user is None:
            logger.warning(
                f"Message {message.id} sent but route/user not found. Skipping notification.")
            return None

        title = "Message delivered"
        message_text = (
            f"A new message was sent through route '{route.label}' and is available for review."
        )
        logger.info(
            f"Message {message.id} sent for user {user.id} "
            f"(route: {route.label})"
        )
        return NotificationService.create(
            user=user,
            notification_type=NotificationType.MESSAGE_SENT,
            title=title,
            message=message_text,
            content_object=message,
        )

    @staticmethod
    def message_failed(message, reason=None):
        route = getattr(message, 'apikey', None).route if getattr(
            message, 'apikey', None) else None
        user = route.user if route is not None else None
        if user is None:
            logger.warning(
                f"Message {message.id} failed but route/user not found. Skipping notification.")
            return None

        title = "Message delivery failed"
        message_text = (
            f"A message sent through route '{route.label}' failed."
            + (f" Reason: {reason}" if reason else "")
        )
        logger.error(
            f"Message {message.id} delivery failed for user {user.id} "
            f"(route: {route.label}, reason: {reason})"
        )
        return NotificationService.create(
            user=user,
            notification_type=NotificationType.MESSAGE_FAILED,
            title=title,
            message=message_text,
            content_object=message,
        )
