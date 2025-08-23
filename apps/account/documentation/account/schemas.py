from drf_spectacular.utils import extend_schema, extend_schema_view ,OpenApiExample,OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from apps.account.serializers import ( 
  UserSerializer, LoginSerializer, LogoutSerializer, OTPSerializer,EmailSerializer,PasswordResetSerializer,
  ProfileSerializer
                                      )
from apps.account.documentation.account.docstrings import (
    REGISTER_USER_DESCRIPTION, LOGIN_VIEW_DESCRIPTION, LOGIN_USER_200_OK, LOGIN_USER_400_BAD_REQUEST, LOGOUT_USER_DESCRIPTION,
    REGISTER_USER_CREATED, REGISTER_USER_BAD_REQUEST, VERIFY_EMAIL_OTP_DESCRIPTION, VERIFY_EMAIL_OTP_FAILURE_RESPONSE,
    VERIFY_EMAIL_OTP_SUCCESS_RESPONSE, VERIFY_EMAIL_OTP_USER_NOT_FOUND_RESPONSE, RESEND_OTP_DESCRIPTION, RESEND_OTP_SUCCESS_RESPONSE,
    RESEND_OTP_NOT_FOUND_RESPONSE, RESEND_OTP_ERROR_RESPONSE, PROFILE_REQUEST,  PROFILE_204_RESPONSE, PROFILE_400_RESPONSE, 
    PROFILE_404_RESPONSE, TOKEN_REFRESH_200_OK, TOKEN_REFRESH_DESCRIPTION,TOKEN_REFRESH_400_BAD_REQUEST
)


register_user_doc = extend_schema(
    methods=['POST'],
    summary='User registration endpoint.',
    description=REGISTER_USER_DESCRIPTION,
    request=UserSerializer,
    responses={
        201: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT
    },
    examples=[REGISTER_USER_CREATED, REGISTER_USER_BAD_REQUEST],
    tags=['Authentication']
)


email_verify_otp_doc = extend_schema(
    methods=['POST'],
    summary='Verify email with OTP',
    description=VERIFY_EMAIL_OTP_DESCRIPTION,
    request=OTPSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT
    },
    examples=[VERIFY_EMAIL_OTP_SUCCESS_RESPONSE,
              VERIFY_EMAIL_OTP_FAILURE_RESPONSE, VERIFY_EMAIL_OTP_USER_NOT_FOUND_RESPONSE],
    tags=['Authentication']
)


resend_email_otp_doc = extend_schema(
    methods=['POST'],
    summary='Resend OTP for email verification',
    description=RESEND_OTP_DESCRIPTION,
    request=EmailSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
        500: OpenApiTypes.OBJECT
    },
    examples=[
        RESEND_OTP_SUCCESS_RESPONSE,
        RESEND_OTP_NOT_FOUND_RESPONSE,
        RESEND_OTP_ERROR_RESPONSE
    ],
    tags=['Authentication']
)


login_user_doc = extend_schema(
    methods=['POST'],
    summary='User login endpoint.',
    description=LOGIN_VIEW_DESCRIPTION,
    request=LoginSerializer,
    responses={
      200:OpenApiTypes.OBJECT,
      400:OpenApiTypes.OBJECT},
    examples=[LOGIN_USER_200_OK,LOGIN_USER_400_BAD_REQUEST],
    tags=['Authentication']

)

refresh_token_doc = extend_schema_view(
    post=extend_schema(
        methods=['POST'],
        summary='Token refresh endpoint to get new access token',
        description=TOKEN_REFRESH_DESCRIPTION,
        request=LogoutSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT
        },
        examples=[TOKEN_REFRESH_200_OK, TOKEN_REFRESH_400_BAD_REQUEST],
        tags=['Token']
    )
)



logout_user_doc = extend_schema(
    methods=['POST'],
    summary='Logout user. You must be logged in to access this endpoint',
    description=LOGOUT_USER_DESCRIPTION,
    request=LogoutSerializer,
    responses={
        205: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT
    },
    tags=['Authentication'],
    examples=[
        OpenApiExample(
            'Logout Response',
            value={'message': 'Logout successful'},
            response_only=True,
            status_codes=['205'],
        ),
        OpenApiExample(
            'Error Response',
            value={'error': 'Token is invalid or expired'},
            response_only=True,
            status_codes=['400'],
        ),
    ]
)


password_reset_otp_doc = extend_schema(
    summary="Request Password Reset send reset OTP and url to mail ",
    description=(
        "Public endpoint to request a password reset OTP. "
        "Accepts an email address and sends an OTP to the user if the email is associated with an account. "
        "Response is the same regardless of whether the email exists (for security)."
    ),
    request=EmailSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        500: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            "Successful request (email exists or not)",
            value={"message": "Password reset OTP sent if email exists. Check email and follow the link"},
            status_codes=["200"],
            response_only=True
        ),
        OpenApiExample(
        '500 INTERNAL SERVER ERROR',
        summary='Error generating OTP or sending email',
        description='There was an internal error while trying to reset password with OTP.',
        value={
            "message": "Failed to resend OTP: <error_message> either mail not send "
        },
        status_codes=['500'],
        response_only=True
)
        
    ],
    tags=["Authentication & Password Reset"],
)


password_reset_verify = extend_schema(
    summary="Verify OTP and reset password",
    description="""
    Public endpoint to verify a one-time password (OTP) sent to a user's email address for password reset.
    
    The user provides:
    - `email` (as query parameter),
    - `otp`,
    - `new_password`,
    - `confirm_password` (inside the request body).

    If the OTP is valid and matches the one stored for the given email, the user's password is updated.

    Responses:
    - `200 OK` - Password successfully updated.
    - `400 Bad Request` - Invalid or expired OTP, or validation errors.
    - `404 Not Found` - User with the given email does not exist.
    """,
    request=PasswordResetSerializer,
    responses={
        200: OpenApiResponse(
            description="Password updated successfully. Kindly login.",
            examples=[
                {
                    "value": {"message": "Password updated successfully. Kindly login"},
                    "summary": "Password successfully reset"
                }
            ]
        ),
        400: OpenApiResponse(
            description="OTP invalid or expired.",
            examples=[
                {
                    "value": {"message": "Invalid or expired OTP"},
                    "summary": "Invalid OTP"
                }
            ]
        ),
        404: OpenApiResponse(
            description="User not found for provided email.",
            examples=[
                {
                    "value": {"message": "User not found"},
                    "summary": "User not found"
                }
            ]
        ),
    },
    tags=["Authentication & Password Reset"]
)


profile_doc = extend_schema_view(
    get=extend_schema(
        summary='Retrieve a profile by ID.',
        description='Endpoint to retrieve a profile by their unique ID by the user or admin. User must be authenticated(logged in ) to view their profile',
        responses={404:OpenApiTypes.OBJECT},
        examples=[PROFILE_404_RESPONSE],
        tags=['Profiles'],
    ),
    patch=extend_schema(
        summary='Partially update a profile.',
        description='Endpoint to partially profile details. Include the field to be updated field alone in the body. Must be authenticated to perform the action',
        request=OpenApiTypes.OBJECT,
        responses={200: ProfileSerializer},
        examples=[PROFILE_REQUEST],
        tags=['Profiles'],
    ),
    delete=extend_schema(
        summary='Delete a profile to remove the user.',
        description='Endpoint to remove a profile by ID.',
        responses={
            204: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT
        },
        examples=[PROFILE_204_RESPONSE, PROFILE_404_RESPONSE],
        tags=['Profiles'],
    ),
)
