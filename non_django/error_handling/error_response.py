from project_settings.server.server_configuration import INSTALLED_APPS_SERVER
import logging
import sys
logging.basicConfig()
logger = logging.getLogger(__name__)

__author__ = 'ahmad'


class ErrorResponse(object):

    def __init__(self, app_code=None, error_code=None, error_message=None, log_id=''):
        self.app_code = app_code
        self.error_code = error_code
        self.error_message = error_message
        self.log_id = log_id

    def get_error_response_data(self, app_name):
        response = {
            'app_code': self.app_code if self.app_code else self.get_app_code(app_name),
            'error_code': self.error_code,
            'error_message': self.error_message,
            'log_id': self.log_id
        }
        return response

    def set_error_data_simple(self, error_code=None, error_message=None):
        self.error_message =error_message
        self.error_code = error_code

    def set_error_data(self, error):
        if isinstance(error, dict):
            self.error_code = list(error.keys())[0]
            self.error_message = list(error.values())[0]
        else:
            try:
                raise ValueError('Wrong Data type passed to get_error_data method')
            except ValueError as e:
                logger.error(sys.exc_traceback.tb_lineno)
                logger.error(type(e))
                logger.error(e.message)

    @staticmethod
    def get_app_code(app_name):
        # eg: app_name = backend_apps.aoi_site.views => backend_apps.aoi_site
        app_name_split = app_name.split('.')
        app_name_res = app_name_split[0]
        for index in range(1, len(app_name_split)):
            if 'views' not in app_name_split[index]:
                app_name_res += '.' + app_name_split[index]
        if 'models' in app_name_split:
            app_name_split.remove('models')
            app_name_res = '.'.join(app_name_split)

        code = [list(app.keys())[0] for app in INSTALLED_APPS_SERVER if list(app.values())[0] == app_name_res][0]
        return code


error_response = ErrorResponse()
