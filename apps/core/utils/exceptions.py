import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response

logger = logging.getLogger('apps')


def global_exception_handler(exc, context):
    # Call DRF's default handler first
    response = exception_handler(exc, context)

    if response is None:
        # 500 Internal Server Error (Database down, code crash, etc.)
        logger.error(f"Critical Exception: {exc}", exc_info=True)
        return Response({
            "status": "error",
            "message": "A server error occurred."
        }, status=500)

    # Log standard API errors (400, 401, 403, 404)
    logger.warning(f"API Error at {context['view'].__class__.__name__}: {exc}")

    error_payload = {
        "status": "error",
        "message": "An error occurred.",
        "details": response.data
    }

    if isinstance(response.data, dict):
        if not response.data:
            error_payload["message"] = "No additional error details provided."
        else:
            # Flatten the first error into a string for the toast/alert
            first_field = next(iter(response.data))
            first_val = response.data[first_field]

            # If it's a list (typical DRF), get the first item
            if isinstance(first_val, list) and len(first_val) > 0:
                msg = str(first_val[0])
            else:
                msg = str(first_val)

            # Standardize message: "Email: user already exists"
            error_payload["message"] = f"{first_field.capitalize()}: {msg}"

    elif isinstance(response.data, list) and len(response.data) > 0:
        error_payload["message"] = str(response.data[0])

    response.data = error_payload
    return response
