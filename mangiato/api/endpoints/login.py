"""
This module contains class and methods related to login of users. Generate the
token for users can operate in Mangiato API
"""

from flask import jsonify, g
from flask_restplus import Resource
from mangiato.api.restplus import API
from mangiato.api.serializers import LOGIN_MODEL
from mangiato.constants import API_VERSION, CODE_OK, CODE_UNAUTHORIZED
from mangiato.globals import AUTH


LOGIN_NS = API.namespace(API_VERSION + 'login', description='Endpoint to log '
                                                            'users.')


@LOGIN_NS.route('/', strict_slashes=False)
class Login(Resource):
    """
    Represent resource corresponding to endpoint login
    """
    @staticmethod
    @API.response(CODE_OK, "Login successful", LOGIN_MODEL)
    @API.response(CODE_UNAUTHORIZED, '{"error": "Unauthorized access"}')
    @AUTH.login_required
    def post():
        """
        Respond to a post method for /login endpoint, when an user wants to
        log in the server.
        :return: Response containing the valid token for the user and time
        validation of token. A error message in case the user is not
        registered or if it provide an incorrect password. The HTTP code.
        :rtype: tuple(json, int)
        """

        token = g.user.generate_auth_token(600)
        return jsonify({'token': token, 'duration': 600})
