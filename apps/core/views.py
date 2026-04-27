from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Notification
from .pagination import NotificationPagination
from .serilalizer import NotificationSerializer, NotificationListSerializer



class NotificationListView(ReadOnlyModelViewSet):
    # Fix 1: Provide a base queryset and lookup_field for schema generation
    queryset = Notification.objects.all()
    lookup_field = 'id'
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationListSerializer
        return NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        unread_count = queryset.filter(is_read=False).count()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "results": serializer.data,
                "unread_count": unread_count
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "results": serializer.data,
            "unread_count": unread_count
        })

    def retrieve(self, request, *args, **kwargs):
        notification = self.get_object()

        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])

        serializer = self.get_serializer(notification)
        return Response(data={
            "message": "Notification retrieved successfully",
            "notification": serializer.data
        }, status=200)

    @action(detail=True, methods=['post'])
    def read(self, request, *args, **kwargs):
        notification = self.get_object()

        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])

        return Response(data={
            "message": "Notification marked as read successfully",
        }, status=200)

    @action(detail=True, methods=['post'])
    def unread(self, request, *args, **kwargs):
        notification = self.get_object()

        if notification.is_read:
            notification.is_read = False
            notification.save(update_fields=["is_read"])

        return Response(data={
            "message": "Notification marked as unread successfully",
        }, status=200)
