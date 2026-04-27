from drf_spectacular.utils import OpenApiExample


ROUTE_400 = OpenApiExample(
    '400 BAD REQUEST',
    summary='Invalid input data',
    description='The request contains invalid or missing fields.',
    value={
        "recipient_email": ["This field is required."]
    },
    response_only=True,
    status_codes=["400"]
)

ROUTE_404 = OpenApiExample(
    '404 NOT FOUND',
    summary='Route not found',
    description='No route found with the specified ID.',
    value={
        "detail": "Not found."
    },
    response_only=True,
    status_codes=["404"]
)

ROUTE_500 = OpenApiExample(
    '500 INTERNAL SERVER ERROR',
    summary='Unexpected error occurred',
    description='A server error occurred. Please try again later.',
    value={
        "detail": "Internal server error"
    },
    response_only=True,
    status_codes=["500"]
)

ROUTE_204 = OpenApiExample(
    '204 NO CONTENT',
    summary='Route deleted',
    description='The route was successfully deleted. No content is returned.',
    value=None,
    response_only=True,
    status_codes=["204"]
)

MESSAGE_404 = OpenApiExample(
    '404 NOT FOUND',
    summary='Message not found',
    description='The requested message could not be found.',
    value={"detail": "Not found."},
    response_only=True,
    status_codes=["404"]
)

MESSAGE_500 = OpenApiExample(
    '500 INTERNAL SERVER ERROR',
    summary='Unexpected server error',
    description='An unexpected error occurred.',
    value={"detail": "Internal server error"},
    response_only=True,
    status_codes=["500"]
)


SEND_EMAIL_200 = OpenApiExample(
    "Successful Message Send",
    value={
        "detail": "Message sent successfully.",
        "preview_link": "../messages/123/",
        "api_key_prefix": "8h97nI"
    },
    response_only=True,
    status_codes=["200"],
)

SEND_EMAIL_400 = OpenApiExample(
    "Validation Error (missing required field or spam)",
    value={
        "detail": "Validation failed",
        "errors": {
            "visitor_email": ["This field is required."]
        }
    },
    response_only=True,
    status_codes=["400"],
)

SEND_EMAIL_401 = OpenApiExample(
    "Invalid API Key",
    value={"detail": "Invalid or missing API key"},
    response_only=True,
    status_codes=["401"],
)

SEND_EMAIL_403 = OpenApiExample(
    "Revoked API Key",
    value={"detail": "API key revoked or inactive"},
    response_only=True,
    status_codes=["403"],
)

SEND_EMAIL_429 = OpenApiExample(
    "Rate Limit Exceeded",
    value={"detail": "Too many requests, please try again later."},
    response_only=True,
    status_codes=["429"],
)

SEND_EMAIL_500 = OpenApiExample(
    "Unexpected Server Error",
    value={"detail": "An unexpected error occurred"},
    response_only=True,
    status_codes=["500"],
)


# Successful creation with raw keys returned once
ROUTEAPIKEY_CREATE_201_RESPONSE = OpenApiExample(
    '201 CREATED',
    description='Successfully created a route and generated API keys (one-time raw keys).',
    value={
        "id": 11,
        "label": "Contact",
        "channel": "email",
        "is_active": True,
        "config": {"recipient_emails": ["edupima@gmail.com", "pima@gmail.com"]},
        "is_deleted": False,
        "deleted_at": None,
        "created_at": "2026-04-07T12:24:40.164605Z",
        "api_keys": {
            "test":
            {
                "id": 16,
                "prefix": "ii_test_3YixkE",
                "env_choices": "test",
                "is_active": True,
                "usage_count": 0,
                "last_used_at": None,
                "created_at": "2026-04-07T12:24:40.164605Z",
                "key": "ii_test_rY7AnEpSt7DOJXNNZNkdNbB0cGvcU3zylDYQF3YixkE",
            },
            "live":
            {
                "id": 17,
                "prefix": "ii_live_yqHbuw",
                "env_choices": "live",
                "is_active": True,
                "usage_count": 0,
                "last_used_at": None,
                "created_at": "2026-04-07T12:24:40.179366Z",
                "key": "ii_live_tDMENbh7lnNOqrX7lXDDHBL_ZF9KVyp0kmzA_yqHbuw",
            }
        }
    },
    response_only=True,
    status_codes=['201']
)

ROUTEAPIKEY_UPDATE_200_RESPONSE = OpenApiExample(
    '200 OK',
    description='Successfully updated the route.',
    value={
        "id": 13,
        "label": "Contact",
        "user": {
            "id": "ce7e4cc5-f6ac-4118-bab7-b64771c163df",
            "user": "intern@gmail.com"
        },
        "channel": "email",
        "is_active": True,
        "recipient_emails": None,
        "config": {
            "recipient_emails": [
                "edupima@gmail.com",
                "pima@gmail.com"
            ]
        },
        "is_deleted": False,
        "deleted_at": None,
        "created_at": "2026-04-08T11:01:44.724515Z",
        "api_keys": {
            "live": {
                "id": 21,
                "route": 13,
                "prefix": "ii_live_5bZ7t0",
                "is_active": True,
                "env_choices": "live",
                "channel": "email",
                "usage_count": 0,
                "last_used_at": None,
                "created_at": "2026-04-08T11:01:44.737496Z"
            },
            "test": {
                "id": 20,
                "route": 13,
                "prefix": "ii_test_xwSpnQ",
                "is_active": True,
                "env_choices": "test",
                "channel": "email",
                "usage_count": 0,
                "last_used_at": None,
                "created_at": "2026-04-08T11:01:44.730270Z"
            }
        }
    },
    response_only=True,
    status_codes=['200']
)


# Validation error (missing recipient_emails)
ROUTEAPIKEY_CREATE_400_RESPONSE = OpenApiExample(
    '400 BAD_REQUEST',
    description='Occurs when required fields are missing or invalid.',
    value={
    "config": {
                "recipient_emails": "Invalid email:  `popoolatemilorungail.com`  or This field is required for email channel"
        }
    },
    response_only=True,
    status_codes=['400']
)

# 204 soft delete
ROUTEAPIKEY_DELETE_204_RESPONSE = OpenApiExample(
    '204 NO CONTENT',
    description='Successfully soft deleted. No content is returned but the route still exists.',
    value=None,
    response_only=True,
    status_codes=['204']
)
