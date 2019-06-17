"""
Provide instance of API
"""
from flask_restplus import Api

AUTHORIZATIONS = {
    'basicAuth': {
        'type': 'basic',
        'in': 'header',
        'name': 'Authorization'
    }
}

API = Api(version='1.0', title='Mangiato API',
          description='API where user can register meals and calories',
          authorizations=AUTHORIZATIONS, security='basicAuth')


@API.errorhandler
def default_error_handler():
    """
    Manage default global errors of not manage exceptions
    :return: json error message
    """
    message = 'An unhandled exception occurred.'
    return {'message': message}, 500
