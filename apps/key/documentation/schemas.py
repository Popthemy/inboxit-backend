from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from apps.key.serializers import ListApiKeySerializer, ApiKeySerializer
from .docs import APIKEY_201, ACTIVE_APIKEY_EXIST_400, APIKEY_REVOKED_200, APIKEY_404, APIKEY_ERROR_400


list_apikey_docs = extend_schema_view(
    get=extend_schema(
        summary='Retrieve all API keys',
        description=(
            'Returns a list of all API keys owned by the authenticated user.\n\n'
            'You can search by `prefix`, and order results by `is_active` or `created_at`.\n\n'
            'To sort descending, prefix the field name with a dash (`-`).\n'
            'Example: `?ordering=-created_at`'
        ),
        responses={200: ListApiKeySerializer(many=True)},
        tags=['Apikeys'],
        parameters=[
            OpenApiParameter(
                name='search',
                description='Search by API key prefix (case-insensitive).',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='ordering',
                description='Order by `is_active` or `created_at`. Use `-` prefix for descending order.',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
        ]
    ),
    post=extend_schema(
        summary='Create a new API key',
        description=(
            'Creates a new API key linked to a route **that currently has no active key**.\n\n'
            'Each API key is tied to a route, and only one active key per route is allowed.\n\n'
            '**Important:** The API key is returned only once. Make sure to copy the 64-character key immediately after creation.'
        ),
        request=ApiKeySerializer,
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT
        },
        examples=[APIKEY_201, ACTIVE_APIKEY_EXIST_400],
        tags=['Apikeys']
    )
)

details_apikey_docs = extend_schema_view(
  get=extend_schema(
    summary='Retrieve an apikey with the ID belonging to the authenticated user.',
    description='Retrieve the ID of apikey that belong to your in the url.',
    responses={200: ApiKeySerializer, 400: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT},
    examples=[APIKEY_404, APIKEY_ERROR_400],
    tags=['Apikeys']
  ),
  post=extend_schema(
    summary='Revoke the retrieved apikey',
    description='Revoke the retrieved apikey by making its inactive, unable to be used to route message. No body required. Works like deleting',
    responses={200: OpenApiTypes.OBJECT,
               400: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT},
    examples=[APIKEY_REVOKED_200,  APIKEY_ERROR_400, APIKEY_404],
    tags=['Apikeys']
  )
)