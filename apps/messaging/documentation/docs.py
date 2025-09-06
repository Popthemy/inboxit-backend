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
