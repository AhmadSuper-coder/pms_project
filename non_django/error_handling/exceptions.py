import sys
import logging
import traceback

from rest_framework.response import Response
from rest_framework import status
from non_django.error_handling.error_response import error_response


logging.basicConfig()
logger = logging.getLogger(__name__)
__author__ = 'ahmad'



class GlobalException(Exception):
    INVALID_URL = {
        5003: 'Url is invalid.'
    }

    DEFAULT = {
        5000: 'Unexpected error occurred. Please try again or send us feedbacks.'
    }
    
    # generic error and codes for similar kind of errors
    GENERIC_ERROR_CODES = {
        "required": {
            "code": 3001,
            "message": " is required"
        },
        "invalid": {
            "code": 3002,
            "message": " is invalid"
        },
        "not_found": {
            "code": 3003,
            "message": " not found"
        },
        "blank": {
            "code": 3004,
            "message": " can not be blank"
        },
        "internal": {
            "code": 3501,
            "message": "internal server error"
        }
    }

    def get_exception_type_from_code(self, code):
        for key, value in vars(self.__class__).items():
            if isinstance(value, dict):
                if list(value.keys())[0] == code:
                    return value
        return self.DEFAULT

    def make_modified_exception(self, exception, *args, **kwargs):
        exception[list(exception.keys())] = exception.values[0].format(*args, **kwargs)
        return exception

    def get_exception_value_from_exception_dict(self, exception):
        return list(exception.keys())[0]

    def response(self, message, name):
        try:
            if isinstance(message, dict):
                error_response.set_error_data(message)
                return Response(error_response.get_error_response_data(name), status=status.HTTP_400_BAD_REQUEST)
            else:
                raise ValueError('Wrong Exception passed')
        except ValueError as e:
            logger.error(sys.exc_info())
            logger.error(type(e))


    # function to generate generic errors for similar errors ... EX- required / invalid
    def generic(self, error_type="internal", field=None, error_code=None, message=None):
        response = {}
        error_code = error_code or self.GENERIC_ERROR_CODES[error_type]["code"]
        if error_type == "internal":
            response[error_code] = self.GENERIC_ERROR_CODES[error_type]["message"]
        else:
            response[error_code] = field + self.GENERIC_ERROR_CODES[error_type]["message"]
        return response

    @staticmethod
    def print_exception_details(exception):
        """
        prints exception detials
        """
        logging.error(traceback.format_exc())
        logging.error(type(exception))
        if exception.args and len(exception.args) >= 1:
            logging.error(exception.args[0])

    @staticmethod
    def print_exception_details_info(exception):
        """
        prints detail exception
        """
        logging.info(traceback.format_exc())
        logging.info(type(exception))
        if exception.args and len(exception.args) >= 1:
            logging.info(exception.args[0])
    # logging.error(exception.args[0])

def generic_validation_error(self, error_message, error_item_name, app_name):
    response = {}
    error_code = 22  #Just random error code
    error_response.set_error_data_simple(error_message= error_item_name + ":" + error_message,error_code=error_code)
    return Response(error_response.get_error_response_data(app_name),status=status.HTTP_400_BAD_REQUEST)

# function to handle generic errors for multiple fields..either a field or list can be passed
def generic_exception(model, obj, error_type="required", field=None, fields=[], params=[]):
    if field:
        raise model(obj.generic(error_type, field))
    for field in fields:
        if field not in params:
            raise generic_exception(model, obj, error_type, field=field)
