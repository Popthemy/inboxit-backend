from drf_spectacular.utils import OpenApiExample, extend_schema
from apps.analytics.serializers import DashboardMetricsSerializer

dashboard_metric_doc = extend_schema(
    "Dashboard metrics",
    description="return metrics such as total message, active apikey and ...",
    responses=DashboardMetricsSerializer,
    examples=[
        OpenApiExample(
            "Dashboard Example",
            value={
                "totals": {
                    "messages": 12847,
                    "messages_today": 523,
                    "active_api_keys": 8,
                    "active_routes": 5,
                },
                "rates": {
                    "success": 94.9,
                    "failed": 5.1,
                },
                "recent_activity": [
                    {
                        "id": 1,
                        "status": "success",
                        "subject": "title of message",
                        "created_at": "2026-04-21T10:00:00Z"
                    }
                ],
                "messages_per_day": [
                    {"day": "2026-04-15", "count": 120}
                ],
                "messages_per_route": [
                    {
                        "route__id": 1,
                        "route__label": "Email API",
                        "count": 5400
                    }
                ]
            },
        )
    ],
)
