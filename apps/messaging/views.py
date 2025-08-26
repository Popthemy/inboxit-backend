from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.messaging.platforms.email.services import send_message_email
from apps.key.authentication import ApiKeyAuthentication
from .models import Route, Message
from .serializers import RouteSerializer, MessageSerializer


# Create your views here.


class RouteViewSet(ModelViewSet):
    """
    Manage delivery routes (e.g., email recipient settings).
    """
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Route.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MessageViewSet(ModelViewSet):
    """
    Handle messages: list, create, preview.
    """
    http_method_names = ['get']
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(apikey__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()
        # Try sending asynchronously (Celery/RQ recommended for scale)
        # send_contact_email(message)


class SendEmailWithApiKeyView(GenericAPIView):
    '''
    TV3kdckXdRRbl3mty5Qn-K9C9j3u8uLVSQB9-OhbRss

    POST /api/send-email/?apikey=...   or header X-Api-Key: ...
    Body: { "name": "...", "email": "...", "message": "..." }
    Uses the API key's route (email recipient).

    the required data:
    recipient_email : comes from the api key, 
    visitor email comes from the data,
    subject heading,
    body :{}
    optinal data:
    attachment, image_url
    '''
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    # def get(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(self.get_queryset())
    #     data = {
    #         'status':'success', 
    #         'data': serializer.data
    #     }
    #     return Response(data=data, status=status.HTTP_200_OK)

    def post(self,request,*args, **kwargs):
        try:

            apikey_obj = request.auth
            route = apikey_obj.route

            if not route or not route.is_active or route.channel.lower() != "email":
                return Response({"detail": "No active email route for this API key."}, status=400)

            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                message = serializer.save(apikey=apikey_obj, recipient_email=route.recipient_email)
                send_message_email(message)
                return Response({'message': f"Message sent successfully with {apikey_obj.user}  apikey prefix{apikey_obj.key_hash[:7]}..." } , status=status.HTTP_200_OK)
            return Response({'message': f"Message not sent successfully with {serializer.errors}  apikey prefix{apikey_obj.key_hash[:7]}..." } , status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

