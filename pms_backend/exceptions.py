"""
Custom exception handlers for the PMS API.
"""
import logging
from django.http import Http404
from django.core.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    
    Returns appropriate HTTP status codes and error messages for different
    exception types while maintaining security by not exposing sensitive information.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Get the request and view info
    request = context.get('request')
    view = context.get('view')
    
    if response is not None:
        # Customize the error response
        custom_response_data = {
            'error': {
                'status_code': response.status_code,
                'message': get_error_message(response.status_code),
                'details': response.data,
                'timestamp': getattr(request, 'timestamp', None),
            }
        }
        
        # Log the error for debugging
        logger.error(f"API Error {response.status_code}: {response.data}")
        
        response.data = custom_response_data
    
    # Handle Django-specific exceptions
    if isinstance(exc, Http404):
        custom_response_data = {
            'error': {
                'status_code': status.HTTP_404_NOT_FOUND,
                'message': 'Resource not found',
                'details': 'The requested resource does not exist.',
            }
        }
        return Response(custom_response_data, status=status.HTTP_404_NOT_FOUND)
    
    if isinstance(exc, PermissionDenied):
        custom_response_data = {
            'error': {
                'status_code': status.HTTP_403_FORBIDDEN,
                'message': 'Permission denied',
                'details': 'You do not have permission to perform this action.',
            }
        }
        return Response(custom_response_data, status=status.HTTP_403_FORBIDDEN)
    
    # Handle unexpected errors
    if response is None:
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        custom_response_data = {
            'error': {
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'Internal server error',
                'details': 'An unexpected error occurred. Please try again later.',
            }
        }
        return Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response


def get_error_message(status_code):
    """
    Get a user-friendly error message based on HTTP status code.
    """
    error_messages = {
        400: 'Bad request - Invalid input data',
        401: 'Unauthorized - Authentication required',
        403: 'Forbidden - Insufficient permissions',
        404: 'Not found - Resource does not exist',
        405: 'Method not allowed',
        406: 'Not acceptable - Unsupported media type',
        408: 'Request timeout',
        409: 'Conflict - Resource already exists',
        410: 'Gone - Resource no longer available',
        413: 'Payload too large',
        414: 'URI too long',
        415: 'Unsupported media type',
        422: 'Unprocessable entity - Validation failed',
        429: 'Too many requests - Rate limit exceeded',
        500: 'Internal server error',
        501: 'Not implemented',
        502: 'Bad gateway',
        503: 'Service unavailable',
        504: 'Gateway timeout',
    }
    
    return error_messages.get(status_code, 'An error occurred')


class APIException(Exception):
    """
    Base exception class for API-specific errors.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'
    default_code = 'error'

    def __init__(self, detail=None, code=None, status_code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        if status_code is not None:
            self.status_code = status_code

        self.detail = detail
        self.code = code


class ValidationError(APIException):
    """
    Exception for validation errors.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid input.'
    default_code = 'invalid'


class NotFoundError(APIException):
    """
    Exception for resource not found errors.
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found.'
    default_code = 'not_found'


class PermissionError(APIException):
    """
    Exception for permission denied errors.
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Permission denied.'
    default_code = 'permission_denied'
