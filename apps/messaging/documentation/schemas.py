from drf_spectacular.utils import OpenApiExample, extend_schema_view, extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from apps.messaging.Serializers.api_key_and_route_serializer import RouteApiKeySerializer
from apps.messaging.Serializers.main_serializers import UserUsageSerializer, RouteSerializer, MessageSerializer
from .docs import (
    ROUTE_400, ROUTE_404, ROUTE_500, ROUTE_204, MESSAGE_404, MESSAGE_500, ROUTEAPIKEY_CREATE_201_RESPONSE, ROUTEAPIKEY_CREATE_400_RESPONSE, ROUTEAPIKEY_UPDATE_200_RESPONSE, ROUTEAPIKEY_DELETE_204_RESPONSE, SEND_EMAIL_200,
    SEND_EMAIL_400, SEND_EMAIL_401, SEND_EMAIL_403, SEND_EMAIL_429, SEND_EMAIL_500
)

user_usage_doc = extend_schema(
    summary='Retrieve the user usage stats for the overall apikeys',
    description='This show the total number of time messages has been sent using the user api-key',
    tags=['User usage'],
    responses=UserUsageSerializer
)


route_docs = extend_schema_view(
    list=extend_schema(
        summary='List all message delivery routes',
        description=(
            'Retrieves a list of all delivery routes associated with the authenticated user.\n\n'
            'Supports searching by recipient email and ordering by active status.\n\n'
            '**Searchable fields**: `recipient_email`\n'
            '**Orderable fields**: `is_active`\n\n'
            '**Examples:**\n'
            '- `?search=john@example.com`\n'
            '- `?ordering=is_active`\n'
            '- `?ordering=-is_active`'
        ),
        responses={
            200: RouteSerializer(many=True),
            400: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[ROUTE_400, ROUTE_500],
        tags=['Routes'],
        parameters=[
            OpenApiParameter(
                name='search',
                description='Search by recipient email (case-insensitive).',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='ordering',
                description='Order by `is_active`. Use `-` prefix for descending order.',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
        ]
    ),
    retrieve=extend_schema(
        summary='Retrieve a message delivery route',
        description='Returns details of a specific delivery route by ID.',
        responses={
            200: RouteSerializer,
            404: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[ROUTE_404, ROUTE_500],
        tags=['Routes']
    ),
    create=extend_schema(
        summary='Create a new  message delivery route',
        description="""Creates a new delivery route for the authenticated user. The channel has fixed choices check the ChannelEnum to pick a valid choices, 
        recipient emails should be sent as a comma separated string (e.g., "email1@example.com,email2@example.com")""",
        request=RouteSerializer,
        responses={
            201: RouteSerializer,
            400: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[ROUTE_400, ROUTE_500],
        tags=['Routes']
    ),
    partial_update=extend_schema(
        summary='Partially update a message delivery route',
        description='Updates one or more fields of an existing delivery route.',
        request=RouteSerializer,
        responses={
            200: RouteSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[ROUTE_400, ROUTE_404, ROUTE_500],
        tags=['Routes']
    ),
    destroy=extend_schema(
        summary='Delete a message delivery route',
        description='Deletes a specific delivery route by ID.',
        responses={
            204: None,
            404: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[ROUTE_204, ROUTE_404, ROUTE_500],
        tags=['Routes']
    )
)


message_docs = extend_schema_view(
    list=extend_schema(
        summary='List sent messages',
        description=(
            'Returns a list of messages sent via delivery routes.\n\n'
            'You can search by:\n'
            '- `apikey key_hash`\n'
            '- `recipient_email`\n'
            '- `status` (e.g., `sent`, `failed`, `queued`)\n\n'
            '**Example:** `?search=sent`'
        ),
        responses={
            200: MessageSerializer(many=True),
            500: OpenApiTypes.OBJECT
        },
        examples=[MESSAGE_500],
        tags=['Messages'],
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search by `apikey__key_hash`, `recipient_email`, or `status`.'
            )
        ]
    ),
    retrieve=extend_schema(
        summary='Retrieve a single message',
        description='Returns the details and status of a specific message by ID.',
        responses={
            200: MessageSerializer,
            404: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT
        },
        examples=[MESSAGE_404, MESSAGE_500],
        tags=['Messages']
    )
)


send_email_with_apikey_doc = extend_schema(
    summary="Send Email via API Key",
    description=(
        "This endpoint allows you to send emails directly from a static site form or "
        "any backend service by providing an **API key** as a query parameter or in the header.\n\n"
        "### 🔑 Authentication\n"
        "- Each request must include a valid API key in the query string: `?apikey=YOUR_KEY` or in the header `X-API-KEY: YOUR_KEY` \n"
        "- API keys can be revoked through the api detail view.\n\n"
        "### 📦 Required Fields\n"
        "- `visitor_email`: Email of the site visitor submitting the form.\n"
        "- `subject`: Subject of the message.\n"
        "- `body`: Plain text or JSON-formatted string containing the message.\n\n"
        "### 🎛 Optional Fields\n"
        "- `attachments`: List of `{filename, content}` objects (Base64 encoded).\n"
        "- `image_url`: Link to an external image.\n\n"
        "### 🛡️ Spam Protection\n"
        "- Honeypot field: **`website`** — this must be left blank.\n"
        "- If this field contains any value, the request will be rejected as spam.\n\n"
        "### 📡 Example Integration\n"
        "#### HTML Form (easy mode use fetch to prevent redirect):\n"
        "```html\n"
        "<form method='POST' action='https://api.yourdomain.com/api/send-message/?apikey=YOUR_API_KEY'>\n"
        "  <input type='email' name='visitor_email' required>\n"
        "  <input type='text' name='subject' required>\n"
        "  <textarea name='body'></textarea>\n"
        "  <input type='text' name='website' style='display:none'>\n"
        "  <button type='submit'>Send</button>\n"
        "</form>\n"
        "```\n\n"
        "#### JSON Mode (flexible extra fields):\n"
        "```json\n"
        "{\n"
        "  \"visitor_email\": \"jane@example.com\",\n"
        "  \"subject\": \"Product Inquiry\",\n"
        "  \"body\": \"{ \\\"name\\\": \\\"Jane Doe\\\", \\\"message\\\": \\\"Tell me more!\\\" }\",\n"
        "  \"website\": \"\"\n"
        "}\n"
        "```\n\n"
        "### 📊 Rate Limiting\n"
        "This endpoint is been throttled :10 mail per minutes."
    ),
    request=MessageSerializer,
    responses={
        200: OpenApiResponse(
            response=MessageSerializer,
            description="Message successfully sent.",
            examples=[SEND_EMAIL_200],
        ),
        400: OpenApiResponse(
            description="Validation or spam check failed.",
            examples=[SEND_EMAIL_400],
        ),
        401: OpenApiResponse(
            description="Missing or invalid API key.",
            examples=[SEND_EMAIL_401],
        ),
        403: OpenApiResponse(
            description="API key revoked or inactive.",
            examples=[SEND_EMAIL_403],
        ),
        429: OpenApiResponse(
            description="Rate limit exceeded.",
            examples=[SEND_EMAIL_429],
        ),
        500: OpenApiResponse(
            description="Unexpected server error.",
            examples=[SEND_EMAIL_500],
        ),
    },
    parameters=[
        OpenApiParameter(
            name="apikey",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Your API key (must be valid and active)."
        )
    ]
)


route_api_key_docs = extend_schema_view(
    create=extend_schema(
        summary='Create a delivery route  generate API keys.',
        description=(
                'Creates a new route for sending messages (e.g., email). '
                'If api_key data is provided, it generates a test and live key. '
                'Raw keys are returned only once in the response.'
        ),
        request=RouteApiKeySerializer,
        responses={201: RouteApiKeySerializer, 400: OpenApiExample},
        examples=[ROUTEAPIKEY_CREATE_201_RESPONSE,
                  ROUTEAPIKEY_CREATE_400_RESPONSE],
        tags=['Routes Api Keys'],
    ),
    # alllow search mails, filter by active and order by created at
    list=extend_schema(
        summary='List all delivery routes for the authenticated user.',
        description=(
                'Retrieves a list of all delivery routes associated with the authenticated user.\n\n'
                'Supports searching by recipient email and ordering by active status.\n\n'
                '**Searchable fields**: `recipient_email`\n'
                '**Orderable fields**: `is_active`\n\n'
                '**Examples:**\n'
                '- `?search=john@example.com`\n'
                '- `?ordering=is_active`\n'
                '- `?ordering=-is_active`'
                '- `?is_deleted=true`'
        ),
        responses={200: RouteApiKeySerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name='search',
                description='Search by recipient email (case-insensitive).',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='ordering',
                description='Order by `is_active`. Use `-` prefix for descending order.',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='is_deleted',
                description='Filter by deleted status (true or false).',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY
            ),
        ],
        tags=['Routes Api Keys'],
    ),
    retrieve=extend_schema(
        summary='Retrieve a specific route by ID.',
        description='Returns a single route and its API keys (safe info only).',
        responses={200: RouteApiKeySerializer, 404: OpenApiExample},
        tags=['Routes Api Keys'],
    ),
    partial_update=extend_schema(
        summary='Partially update a message delivery route',
        description='Updates one or more fields of an existing delivery route.',
        request=RouteSerializer,
        responses={
                200: RouteApiKeySerializer,
                400: ROUTEAPIKEY_CREATE_400_RESPONSE,
                404: ROUTE_404,
                500: ROUTE_500,
        },
        examples=[ROUTE_400, ROUTE_404, ROUTE_500],
        tags=['Routes Api Keys'],
    ),
    destroy=extend_schema(
        summary='Soft delete a message delivery route',
        description='Soft delete a specific delivery route by ID.',
        responses={
            204: ROUTEAPIKEY_DELETE_204_RESPONSE,
            404: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[ROUTEAPIKEY_DELETE_204_RESPONSE, ROUTE_404, ROUTE_500],
        tags=['Routes Api Keys'],
    )
)
