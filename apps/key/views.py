from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import OrderingFilter,SearchFilter
from apps.key.documentation.schemas import list_apikey_docs, details_apikey_docs
from .serializers import ApiKeySerializer, ListApiKeySerializer
from .models import APIKey, KeyRegenerationLog
from rest_framework.throttling import ScopedRateThrottle
from django.db import transaction
from .utils import check_route_regeneration_limit
"""
You can regenrate only 20 apikey per day and 5 per route
"""


@list_apikey_docs
class ApiKeyView(GenericAPIView):
    """
    
    f53qVR9rSSWibTd9Z1NL162wniyJsNhOled4jUxYbX8
    """

    serializer_class = ListApiKeySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['prefix']
    ordering_fields = ['is_active', 'created_at']

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)

    def get(self, request):
        keys = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(keys, many=True)

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
                'raw_apikey': raw_api_key,
                'data': serializer.data,
            }
            return Response(data=data, status=status.HTTP_201_CREATED)
        return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@details_apikey_docs
class RevokeApiKeyView(GenericAPIView):
    '''
    This endpoint is the details view and can also be used to revoke an api. 
    When you revoke and api you can't receive message using the api
    '''

    serializer_class = ApiKeySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(APIKey, id=self.kwargs.get('pk'), route__user=self.request.user)

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
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, *args, **kwargs):
        '''revoke = delete '''
        try:
            key = self.get_object()
            if key.is_revoked:
                return Response({'message':'key already revoked!'}, status=status.HTTP_200_OK)

            key.revoke()
            serializer = self.get_serializer(key)
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
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RegenerateApiKeyView(GenericAPIView):
    """
    regenarate an apikey it uses the attribute of the the old key 
    e,g it you are regenerating a test key the new key will be a test key attached to the routed.
    ii_test_FxxNGreiiqEfwGB3pz3BXBTIhT3iVKlCNQW_9Xrl0P4
    """
    serializer_class = ApiKeySerializer
    permission_classes = [IsAuthenticated]
    # throttle_scope = "apikey" # 20 per day
    # throttle_classes = [ScopedRateThrottle]

    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            print('from regenerate')
            apikey = get_object_or_404(APIKey, id=self.kwargs.get(
                'pk'), route__user=self.request.user)

            print(apikey)

            # route__user=self.request.user
            route = apikey.route
            env = apikey.env_choice

            # 1. Route-level protection
            check_route_regeneration_limit(route, user)

            with transaction.atomic():

                # 2. Log this regeneration attempt
                KeyRegenerationLog.objects.create(
                    route=route,
                    user=user
                )

                # # 3. Revoke old keys
                # route.keys.filter(
                #     is_active=True,
                #     env_choice__in=env
                # ).update(is_active=False)

                # # 4. Create new key
                # key, raw = APIKey.issue_for(
                #         route=route,
                #         env_choice=env,
                # )

                key, raw = apikey.regenerate()

                new_key = {
                    env: {**self.get_serializer(key).data, "key": raw},
                }

            return Response({
                "status": "success",
                "message": "API keys regenerated successfully",
                "data": new_key
            })

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)