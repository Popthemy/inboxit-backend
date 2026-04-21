from django.core.cache import cache


def invalidate_dashboard_cache(user_id):
    cache.delete(f"dashboard_metrics:{user_id}")
