from drf_spectacular.utils import OpenApiExample


REGISTER_USER_DESCRIPTION = """
    Registers a new user and sends an OTP to their email for verification.

    - When a user signs up, their account is created in an inactive state.
    - An OTP (One-Time Password) is generated and emailed to the user.

    The user must verify their email using the OTP via the /verify-email-otp/ endpoint provided in their mail to activate their account.

    This endpoint allows new (unauthenticated) users to register by providing necessary user information.
    **Permissions**:
        - `IsAnonymous`: Only unauthenticated users are allowed to register.
    """

REGISTER_USER_CREATED = OpenApiExample(
    '201 CREATED',
    description='Registration Successful and mail sent',
    value={'data': {
        'status': 'Success',
        'message': 'Registration successful, please check your email to verify your account.'
        'If you didn\'t receive the OTP, you can use the resend verification link.',
        "data": {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "email": "example@gmail.com",
            "resend verification link": "resend_url"
        }},
    },
    response_only=True,
    status_codes=['201']
)


REGISTER_USER_BAD_REQUEST = OpenApiExample(
    '400 BAD_REQUEST',
    description="If the data is invalid, the serializer will raise an exception, and an appropriate error response will be returned.",
    value={'errors': {"username": ["This field is required."],
                      "password": ["This field is required."],
                      "confirm_password": ["This field may not be blank."],
                      "field": ["Password too common. Use a strong password"],
                      "non_field_errors": [
        "This password is too short.", "It must contain at least 8 characters.",
        "Password and Confirm_password doesn't match."
    ]
    }},
    response_only=True,
    status_codes=['400']
)


VERIFY_EMAIL_OTP_DESCRIPTION = """
    Verifies a user's email address using an OTP sent to their email during registration.

    - Accepts an email in the URL query parameter.
    - Accepts an OTP in the request body.
    - If the OTP is valid and matches the email, the user's account is activated and they can log in.
    - Returns user data and JWT tokens on success.
    This endpoint allows new (unauthenticated) users to register by providing necessary user information.
    **Permissions**:
        - `IsAnonymous`: Only unauthenticated users are allowed to register.
    
"""

VERIFY_EMAIL_OTP_SUCCESS_RESPONSE = OpenApiExample(
    '200 Ok',
    summary='OTP verified and account activated',
    description='The OTP matched and the user account is now active.',
    value={
        "status": "Success",
        "message": "Email verified successfully!",
        "data": {
            "id": "user-id",
            "email": "user@example.com"
            # other details
        },
        "token": {
            "refresh": "refresh_token",
            "access": "access_token"
        }
    },
    status_codes=['200'],
    response_only=True
)

VERIFY_EMAIL_OTP_FAILURE_RESPONSE = OpenApiExample(
    '400 BAD REQUEST',
    summary='OTP failed',
    description='The OTP provided was invalid or has expired.',
    value={
        "message": "Invalid or expired OTP. Generate a new one."
    },
    status_codes=['400'],
    response_only=True
)

VERIFY_EMAIL_OTP_USER_NOT_FOUND_RESPONSE = OpenApiExample(
    '404 NOT FOUND',
    summary='User not found',
    description=' Check if the email belongs to  user.',
    value={
        "message": "User not found"
    },
    status_codes=['404'],
    response_only=True
)


RESEND_OTP_DESCRIPTION = """
    Resend a new OTP (One-Time Password) to the user's email if the previous OTP has expired or is invalid.

    - Accepts the user's email in the request body.
    - If the email exists, a new OTP will be generated and sent to the user's email.
    - The user can then use the new OTP to verify their email.
"""

RESEND_OTP_SUCCESS_RESPONSE = OpenApiExample(
    '200 OK',
    summary='OTP generated and sent successfully',
    description='A new OTP has been generated and sent to the user’s email.',
    value={
        "message": "New OTP generated and sent to mail successfully"
    },
    status_codes=['200'],
    response_only=True,
)

RESEND_OTP_NOT_FOUND_RESPONSE = OpenApiExample(
    '404 Not Found',
    summary='User does not exist',
    description='The provided email does not belong to any registered user.',
    value={
        "message": "User not found."
    },
    status_codes=['404'],
    response_only=True
)

RESEND_OTP_ERROR_RESPONSE = OpenApiExample(
    '500 INTERNAL SERVER ERROR',
    summary='Error generating OTP',
    description='There was an internal error while trying to resend the OTP.',
    value={
        "message": "Failed to resend OTP: <error_message> either mail not send "
    },
    status_codes=['500'],
    response_only=True
)


LOGIN_VIEW_DESCRIPTION = """
    User login endpoint.

    This endpoint allows authenticated users to log in by providing their credentials. 
    The `IsAnonymous` permission class ensures that only unauthenticated users can register through the registration endpoint, 
    but this login endpoint should be used by authenticated users or users trying to log in.

    **Permissions**:
        - `IsAnonymous`: Ensures that only unauthenticated users can access the registration endpoint.
"""


LOGIN_USER_200_OK = OpenApiExample(
    '200 OK',
    description="If the provided credentials are valid, a successful login will return a JWT token and user data.",
    value={
        'status': 'Success',
        'message': 'Welcome back👋',
        "token": {
            "access": "your-access-token-here",
            "refresh": "your-refresh-token-here"
        },
        "data": {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "email": "example@gmail.com"
        }
    },
    status_codes=['200'],
    response_only=True
)


LOGIN_USER_400_BAD_REQUEST = OpenApiExample(
    '400 BAD_REQUEST',
    description="If the login credentials are invalid (e.g., incorrect username/password), an error response will be returned.",
    value={
        'status': 'Error',
        'message': 'Login Unsuccessful',
        'data': {
            'non_field_errors': [
                'Unable to log in with provided credentials.',
                'Invalid username or password.'
            ]
        }
    },
    response_only=True,
    status_codes=['400']
)


TOKEN_REFRESH_DESCRIPTION = """
    Token refresh endpoint.

    This endpoint allows a user to refresh their access token after it has expired, by providing a valid refresh token. 
    The refresh token is used to obtain a new access token without requiring the user to log in again. 
    If the provided refresh token is invalid or expired, an error will be returned.
"""

TOKEN_REFRESH_200_OK = OpenApiExample(
    '200 OK',
    description="If the provided refresh token is valid, a new access token is issued successfully.",
    value={
        'access': 'new-access-token-here'
    },
    response_only=True,
    status_codes=['200']
)


TOKEN_REFRESH_400_BAD_REQUEST = OpenApiExample(
    '400 BAD_REQUEST',
    description="If the provided refresh token is invalid or expired, the token refresh will fail.",
    value={
        'status': 'Error',
        'message': 'Token refresh failed',
        'details': 'Refresh token is invalid or expired.'
    },
    response_only=True,
    status_codes=['400']
)



LOGOUT_USER_DESCRIPTION = """
   Invalidate a refresh token by blacklisting it. Requires authentication. Clients must send the refresh token in the request body.
"""


LOGOUT_USER_200_OK = OpenApiExample(
    '200 OK',
    description="If the refresh token is valid and successfully blacklisted, \
        you can't generate a new access token with that token anymore.",
    value={
        'status': 'Success',
        'message': "Token blacklisted, you can't generate a new access token with that token 😋"
    },
    response_only=True,
    status_codes=['200']
)


LOGOUT_USER_400_BAD_REQUEST = OpenApiExample(
    '400 BAD_REQUEST',
    description="If the refresh token is invalid or the logout operation fails, the response will indicate an error.",
    value={
        'status': 'Error',
        'message': 'Logout failed',
        'details': 'Invalid refresh token'
    },
    response_only=True,
    status_codes=['400']
)


TOKEN_REFRESH_DESCRIPTION = """
    Token refresh endpoint.

    This endpoint allows a user to refresh their access token after it has expired, by providing a valid refresh token. 
    The refresh token is used to obtain a new access token without requiring the user to log in again. 
    If the provided refresh token is invalid or expired, an error will be returned.
"""

TOKEN_REFRESH_200_OK = OpenApiExample(
    '200 OK',
    description="If the provided refresh token is valid, a new access token is issued successfully.",
    value={
        'status': 'Success',
        'message': 'Token refreshed successfully.',
        'access_token': 'new-access-token-here'
    },
    response_only=True,
    status_codes=['200']
)


TOKEN_REFRESH_400_BAD_REQUEST = OpenApiExample(
    '400 BAD_REQUEST',
    description="If the provided refresh token is invalid or expired, the token refresh will fail.",
    value={
        'status': 'Error',
        'message': 'Token refresh failed',
        'details': 'Refresh token is invalid or expired.'
    },
    response_only=True,
    status_codes=['400']
)



PROFILE_REQUEST = OpenApiExample(
    'Profile Payload(body of the request)',
    summary='Request to update',
    description='Request body to profile.',
    value={'middle_name': 'Bridget'},
    request_only=True
)


PROFILE_400_RESPONSE = OpenApiExample(
    '400 BAD REQUEST',
    summary='Missing or invalid details',
    description='Returned when the required fields is missing or invalid.',
    value={'non fields errors': ["This field is required."]},
    response_only=True,
    status_codes=['400']
)


PROFILE_404_RESPONSE = OpenApiExample(
    '404 NOT FOUND',
    summary='user does not have record or matching record.',
    value={"detail": "Profile not found."},
    response_only=True,
    status_codes=['404']
)


PROFILE_204_RESPONSE = OpenApiExample(
    '204 No Content',
    summary='Profile does not exist after deletion',
    value={"detail": "Profile doesn't."},
    status_codes=['204'],
    response_only=True
)
