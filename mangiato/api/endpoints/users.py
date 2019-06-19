"""
This module contains classes and methods related to users registered on
Mangiato API
"""
from flask import request, g
from flask_restplus import Resource
from mangiato.constants import (API_VERSION, CODE_CONFLICT, RESPONSES_CATALOG,
                                CODE_CREATED, CODE_NOT_ACCEPTABLE,
                                CODE_FORBIDDEN, CODE_OK, CODE_NOT_FOUND,
                                CODE_NO_CONTENT)
from mangiato.globals import AUTH
from mangiato.api.business.users import (create_user, confirm_email_business,
                                         get_user, get_users, update_user,
                                         patch_user, delete_user)
from mangiato.api.restplus import API
from mangiato.api.serializers import (NEW_USER_MODEL, USER_DESCRIPTION,
                                      USER_WITH_ENTRIES, USER_DESCRIPTION_PUT,
                                      USER_DESCRIPTION_PATCH)
from mangiato.api.parsers import PAGE_ARGUMENTS_USERS

USERS_NS = API.namespace(API_VERSION + 'users',
                         description='Operations related to users')
USER_NS = API.namespace(API_VERSION + 'users/<int:id_user>',
                        description='Operations related to users')


@USERS_NS.route('/', strict_slashes=False, methods=['POST', 'GET'])
class Users(Resource):
    """
    Represent the module to manage requests to resource corresponding to
    endpoint users/
    """

    @staticmethod
    @API.response(CODE_CONFLICT, str(RESPONSES_CATALOG['existing_user']))
    @API.response(CODE_CREATED, str(RESPONSES_CATALOG['mail_sent']))
    @API.expect(NEW_USER_MODEL, validate=True)
    def post():
        """
        Respond to a post method for /users endpoint to register a new user
        :return: Response successful if the user is not registered,
        error otherwise. HTTP status code
        :rtype: tuple(json, int)
        """
        return create_user(request.json)

    @staticmethod
    @API.response(CODE_NOT_ACCEPTABLE,
                  str(RESPONSES_CATALOG['error_parse_query_values']) + "\n" +
                  str(RESPONSES_CATALOG['error_parse_query_fields']))
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_resource']))
    @API.response(CODE_OK, 'User with role admin', USER_WITH_ENTRIES)
    @AUTH.login_required
    @API.expect(PAGE_ARGUMENTS_USERS, validate=True)
    def get():
        """
        Respond to a get method for /users endpoint to get the list of
        users, this is accessible only for managers and admins
        :return: list of users an roles for managers, adding to this lis of
        meals and roles for admins. HTTP status code
        :rtype: tuple(json, int)
        """
        return get_users(request, g.user)


@USERS_NS.route('/confirm/<string:token>', strict_slashes=False,
                methods=['GET'])
class EmailConfirmation(Resource):
    """
    Represent the module to manage email account confirmation
    """
    @staticmethod
    @API.response(CODE_NOT_FOUND,
                  str(RESPONSES_CATALOG['no_user_link']) + "\n" +
                  str(RESPONSES_CATALOG['invalid_link']))
    @API.response(CODE_OK, 'Form Rendered')
    def get(token):
        """
        Respond to a GET method request for an account of user confirmation
        :param token: token provided by email to the user to confirm the
        registration
        :type: str
        :return: Message of account confirmed is success, error message
        otherwise. HTTP status code.
        :type: tuple(json, int)
        """
        return confirm_email_business(token)


@USER_NS.route('/', strict_slashes=False, methods=['GET', 'PUT', 'PATCH',
                                                   'DELETE'])
class User(Resource):
    """
    Represent the module to manage requests to resource corresponding to
    endpoint users/<id_user>
    """
    @staticmethod
    @API.response(CODE_NOT_FOUND, str(RESPONSES_CATALOG['no_user_server']))
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_resource']))
    @API.response(CODE_OK, 'Success', USER_DESCRIPTION)
    @AUTH.login_required
    def get(id_user):
        """
        Respond to a get method for users/<id_user> endpoint
        to retrieve information of a specific user
        :param id_user: user id coming from url, define the user which the
        request will be done
        :type: int
        :return: user modified if success or an error otherwise. HTTP status
        code
        :rtype: tuple(json,int)
        """
        return get_user(id_user, g.user)

    @staticmethod
    @API.response(CODE_NOT_FOUND, str(RESPONSES_CATALOG['no_user_server']))
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_update_resource']))
    @API.response(CODE_OK, 'Success', USER_DESCRIPTION)
    @AUTH.login_required
    @API.expect(USER_DESCRIPTION_PUT, validate=True)
    def put(id_user):
        """
        Respond to a PUT method for users/<id_user>
        endpoint to modify information of the user, in this
        case all fields of user model must be provided
        :param id_user: username coming from url, define the user which the
        request will be done
        :type: int
        :return: user modified is success or error otherwise. HTTP status code
        :rtype: tuple(json, int)
        """

        return update_user(id_user, request.json, g.user)

    @staticmethod
    @API.response(CODE_NOT_FOUND, str(RESPONSES_CATALOG['no_user_server']))
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_update_resource']))
    @API.response(CODE_OK, 'Success', USER_DESCRIPTION)
    @AUTH.login_required
    @API.expect(USER_DESCRIPTION_PATCH, validate=True)
    def patch(id_user):
        """
        Respond to a PATCH method for users/<id_user>
        endpoint to modify information of the user, in this
        case it can be modified some fields, not all of them necessary
        :param id_user: username coming from url, define the user which the
        request will be done
        :type: int
        :return: user modified is success or error otherwise. HTTP status code
        :rtype: tuple(json, int)
        """
        return patch_user(id_user, request.json, g.user)

    @staticmethod
    @API.response(CODE_NOT_FOUND, str(RESPONSES_CATALOG['no_user_server']))
    @API.response(CODE_NO_CONTENT, str(RESPONSES_CATALOG['user_deleted']) +
                  "\n" +
                  str(RESPONSES_CATALOG['no_permission_delete_resource']))
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_delete_resource']))
    @AUTH.login_required
    def delete(id_user):
        """
        Respond to DELETE method for users/<id_user> endpoint. Delete a user
        :param id_user: username coming from url, define the user which the
        delete action will be done
        :type: int
        :return: empty. HTTP status code
        :rtype: int
        """
        return delete_user(id_user, g.user)
