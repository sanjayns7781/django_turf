from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # two scerio is for handling the situation where DRF recognise the response and not.

    if response is not None:
        # Build custom response format
        custom_response = {
            "error": str(response.data.get('detail', 'An error occurred')),
            "details": response.data if isinstance(response.data, dict) else {},
            "code": response.status_code,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        response.data = custom_response

    else:
        # For unhandled exceptions
        response = Response(
            {
                "error": "Internal Server Error",
                "details": str(exc),
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
