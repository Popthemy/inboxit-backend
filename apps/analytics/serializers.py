# analytics/serializers.py

from rest_framework import serializers


class TotalsSerializer(serializers.Serializer):
    messages = serializers.IntegerField()
    messages_today = serializers.IntegerField()
    active_api_keys = serializers.IntegerField()
    active_routes = serializers.IntegerField()


class RatesSerializer(serializers.Serializer):
    success = serializers.FloatField()
    failed = serializers.FloatField()


class RecentActivitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    subject = serializers.CharField()
    status = serializers.CharField()
    sent_at = serializers.DateTimeField()



class MessagesPerDaySerializer(serializers.Serializer):
    day = serializers.DateField()
    count = serializers.IntegerField()


class MessagesPerRouteSerializer(serializers.Serializer):
    route_id = serializers.IntegerField()
    route_label = serializers.CharField()
    route_is_active = serializers.BooleanField()
    route_created_at = serializers.DateTimeField()
    count = serializers.IntegerField()


class DashboardMetricsSerializer(serializers.Serializer):
    totals = TotalsSerializer()
    rates = RatesSerializer()
    recent_activity = RecentActivitySerializer(many=True)
    messages_per_day = MessagesPerDaySerializer(many=True)
    messages_per_route = MessagesPerRouteSerializer(many=True)
