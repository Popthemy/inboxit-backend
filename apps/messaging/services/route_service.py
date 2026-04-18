from apps.messaging.models import Route
from django.db import transaction
from apps.key.models import APIKey


def create_api_keys(route):
    test_key, test_raw = APIKey.issue_for(route, "test")
    live_key, live_raw = APIKey.issue_for(route, "live")

    return {
        "test": {"id": test_key.id, "key": test_raw},
        "live": {"id": live_key.id, "key": live_raw},
    }


class RouteService:
    @staticmethod
    def create_route(validated_data):
        with transaction.atomic():
            route = Route.objects.create(**validated_data)

            keys = create_api_keys(route)
            return route, keys
