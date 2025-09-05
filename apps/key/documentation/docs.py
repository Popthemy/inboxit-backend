from drf_spectacular.utils import OpenApiExample


APIKEY_201 = OpenApiExample(
    '201 CREATED',
    summary='ApiKey created successfully',
    description='A new apikey has been created with the route, copy your raw apikey. Only the hash and the prefix will be saved.',
    value={
        'status': 'success',
                'message': 'new api keys created successfully',
                'raw_apikey': 'raw_api_key',
                'data': "{... other data}"
    },
    status_codes=['201'],
    response_only=True,
)


ACTIVE_APIKEY_EXIST_400 = OpenApiExample(
    '400 BAD_REQUEST',
    summary='ApiKey created unsuccessfully',
    description='An error has occurred',
    value={
        'message': 'These route still has a valid api key. Use the old Api Key or revoke the old api',
    },
    status_codes=['400'],
    response_only=True,
)

APIKEY_404 = OpenApiExample(
    '404 NOT FOUND',
    summary='ApiKey not found',
    description='Does not exist',
    value={"status": "error",
           "message": "API key not found"
           },
    status_codes=['404'],
    response_only=True,
)


APIKEY_REVOKED_200 = OpenApiExample(
    '200',
    summary='ApiKey revoked successfully',
    value={
        'status': 'success',
        'message': "api keys revoked successfully. You can't use the api for receiving message through its route",
        'data': "{... other data}"
    },
    status_codes=['200'],
    response_only=True,
)

APIKEY_ERROR_400 = OpenApiExample(
    '400 BAD_REQUEST',
    summary='Error',
    description='An error has occurred',
    value={
        'message': 'Some error has occurred',
    },
    status_codes=['400'],
    response_only=True,
)