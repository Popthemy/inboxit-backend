from apps.core.services.notification_service import NotificationService
from apps.core.models import NotificationType
import logging

logger = logging.getLogger(__name__)


class KeyNotificationService:
    @staticmethod
    def api_key_created(api_key):
        user = api_key.route.user
        title = "API key generated"
        message = (
            f"A new {api_key.env_choice} API key was created for your route "
            f"'{api_key.route.label}'."
        )
        logger.info(
            f"API key {api_key.id} created for user {user.id} "
            f"(route: {api_key.route.label}, env: {api_key.env_choice})"
        )
        return NotificationService.create(
            user=user,
            notification_type=NotificationType.API_KEY_CREATED,
            title=title,
            message=message,
            content_object=api_key,
        )

    @staticmethod
    def api_key_regenerated(api_key):
        user = api_key.route.user
        env = api_key.env_choice

        title = "API key regenerated"

        message = (
            f"Your {env} API key for route '{api_key.route.label}' was regenerated "
            f"and is ready to use."
        )

        logger.info(
            f"API key {api_key.id} regenerated for user {user.id} "
            f"(route: {api_key.route.label}, env: {env})"
        )
        return NotificationService.create(
            user=user,
            notification_type=NotificationType.API_KEY_REGENERATED,
            title=title,
            message=message,
            content_object=api_key,
        )

    @staticmethod
    def api_key_revoked(api_key):
        user = api_key.route.user
        env = api_key.env_choice
        title = "API key revoked"

        message = (
            f"{env} API key for route '{api_key.route.label}' was revoked. "
            f"Any requests using that key will stop working."
        )

        logger.info(
            f"API key {api_key.id} revoked for user {user.id} "
            f"(route: {api_key.route.label}, env: {env})"
        )
        return NotificationService.create(
            user=user,
            notification_type=NotificationType.API_KEY_REVOKED,
            title=title,
            message=message,
            content_object=api_key,
        )
