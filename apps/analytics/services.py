# analytics/services.py

from django.utils.timezone import now, timedelta
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.core.cache import cache
from collections import defaultdict

from apps.messaging.models import Message, Route
from apps.key.models import APIKey


CACHE_TIMEOUT = 60  # seconds


def get_dashboard_metrics(user):
    cache_key = f"dashboard_metrics:{user.id}"
    data = cache.get(cache_key)

    if data:
        return data

    base_qs = Message.objects.filter(apikey__route__user=user)

    # ---- totals + success/fail (ONE query)
    stats = base_qs.aggregate(
        total=Count("id"),
        success=Count("id", filter=Q(status="sent")),
        failed=Count("id", filter=Q(status="failed")),
    )

    total = stats["total"] or 0
    success = stats["success"] or 0
    failed = stats["failed"] or 0

    success_rate = (success / total * 100) if total else 0
    failed_rate = (failed / total * 100) if total else 0

    # ---- today count
    today = now().date()

    messages_today = base_qs.filter(
        sent_at__date=today
    ).count()

    # ---- recent activity
    recent = list(
        base_qs
        .order_by("-sent_at")
        .values("id","subject", "status", "sent_at")[:5]
    )

    # ---- messages per day (last 7 days)
    last_7_days = now() - timedelta(days=7)

    raw_daily = (
        base_qs
        .filter(sent_at__gte=last_7_days)
        .annotate(day=TruncDate("sent_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    daily_map = defaultdict(int)
    for row in raw_daily:
        daily_map[row["day"]] = row["count"]

    messages_per_day = []
    for i in range(7):
        d = (today - timedelta(days=6 - i))
        messages_per_day.append({
            "day": d,
            "count": daily_map[d]
        })

    # ---- messages per route
    messages_per_route = list(
        base_qs
        .values("apikey__route__id", "apikey__route__label", "apikey__route__is_active", "apikey__route__created_at")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # ---- active api keys
    active_keys = APIKey.objects.filter(
        route__user=user,
        is_active=True
    ).count()

    # ---- active routes
    active_routes = Route.objects.filter(
        user=user,
        is_active=True
    ).count()

    cleaned = [
        {
            "route_id": row["apikey__route__id"],
            "route_label": row["apikey__route__label"],
            "route_is_active": row["apikey__route__is_active"],
            "route_created_at": row["apikey__route__created_at"],
            "count": row["count"],
        }
        for row in messages_per_route
    ]


    data = {
        "totals": {
            "messages": total,
            "messages_today": messages_today,
            "active_api_keys": active_keys,
            "active_routes": active_routes,
        },
        "rates": {
            "success": round(success_rate, 2),
            "failed": round(failed_rate, 2),
        },
        "recent_activity": recent,
        "messages_per_day": messages_per_day,
        "messages_per_route": cleaned,
    }

    cache.set(cache_key, data, CACHE_TIMEOUT)

    return data

