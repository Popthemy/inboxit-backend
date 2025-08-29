from django.db import transaction
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from apps.messaging.platforms.email.services import send_message_email, increment_user_usage
from apps.key.authentication import ApiKeyAuthentication
from .models import Route, Message, UserUsage
from .serializers import RouteSerializer, MessageSerializer, UserUsageSerializer

# Create your views here.


class UserUsageViewSet(ReadOnlyModelViewSet):
    serializer_class = UserUsageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user, _ = UserUsage.objects.get_or_create(user=self.request.user)
        return [user]


class RouteViewSet(ModelViewSet):
    """
    Manage delivery routes (e.g., email recipient settings).
    """
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Route.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()


class MessageViewSet(ModelViewSet):
    """
    Handle messages: list, create, preview.
    """
    http_method_names = ['get']
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['apikey__key_hash', 'recipient_email', 'status']

    def get_queryset(self):
        return Message.objects.filter(apikey__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()


class SendEmailWithApiKeyView(GenericAPIView):
    """
    TV3kdckXdRRbl3mty5Qn-K9C9j3u8uLVSQB9-OhbRss

     Required:
    - visitor_email (from request.data)
    - subject
    - body (can be plain text)

    Optional:
    - attachments (list of {filename, content})
    - image_url

    Spam Protection:
    - Honeypot field: `website` (must be blank)

    The recipient_email is derived from the route tied to the API key.

    """

    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'send_email_with_apikey'
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def post(self, request, *args, **kwargs):
        apikey_obj = request.auth
        route = apikey_obj.route

        if not route or not route.is_active or route.channel.lower() != "email":
            return Response({"detail": "No active email route for this API key."}, status=400)

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"detail": "Validation failed", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                message = serializer.save(
                    apikey=apikey_obj, recipient_email=route.recipient_email)

                send_message_email(message)
                increment_user_usage(apikey_obj)

                return Response({
                    "detail": f"Message sent successfully.",
                    "preview_link": message.get_absolute_url(),
                    "api_key_prefix": apikey_obj.key_hash[:6]
                }, status=status.HTTP_200_OK)

        except Exception as e:
            print({"error": str(e)})
            return Response(
                {"detail": "An unexpected error occurred", },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
