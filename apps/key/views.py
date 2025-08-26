from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .serializers import ApiKeySerializer, CreateApiKeySerializer, UserUsageSerializer
from .models import APIKey, UserUsage

# Create your views here.


class ApiKeyView(GenericAPIView):
    serializer_class = CreateApiKeySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)

    def get(self, request):
        keys = self.get_queryset()
        serializer = ApiKeySerializer(keys, many=True)

        data = {
            'status': 'success',
            'message': 'api keys fetched successfully ',
            'data': serializer.data,
        }
        return Response(data=data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            key, raw_api_key = serializer.save(user=request.user)
            serializer = ApiKeySerializer(key)

            data = {
                'status': 'success',
                'message': 'new api keys created successfully',
                'api_key': raw_api_key,
                'data': serializer.data,
            }
            return Response(data=data, status=status.HTTP_201_CREATED)
        return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class RevokeApiKeyView(GenericAPIView):
    '''
    This endpoint is the details view and can also be used to revoke an api. 
    When you revoke and api you can't receive message using the api
    '''
    serializer_class = ApiKeySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):

        return get_object_or_404(APIKey, id=self.kwargs.get('pk'), user=self.request.user)

    def get(self, *args, **kwargs):
        try:
            key = self.get_object()
            serializer = self.get_serializer(key)
            data = {
                'status': 'success',
                'message': 'api keys retrieved successfully',
                'data': serializer.data,
            }
            return Response(data=data, status=status.HTTP_200_OK)

        except Http404:
            return Response({
                'status': 'error',
                'message': 'API key not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': e}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, *args, **kwargs):
        try:
            key = self.get_object()
            print(f'{key} revoked')
            key.revoke()
            serializer = self.get_serializer(self.get_object())
            data = {
                'status': 'success',
                'message': "api keys revoked successfully. You can't use the api for receiving message through its route",
                'data': serializer.data,
            }
            return Response(data=data, status=status.HTTP_200_OK)

        except Http404:
            return Response({'status': 'error', 'message': 'API key not found'
                             }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': e}, status=status.HTTP_400_BAD_REQUEST)


class UserUsageViewSet(ReadOnlyModelViewSet):
    serializer_class = UserUsageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user , _ =UserUsage.objects.get_or_create(user=self.request.user)
        print(user)
        return [user]
