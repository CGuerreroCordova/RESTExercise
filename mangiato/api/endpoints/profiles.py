"""
This module contains class and methods to manage profile of users
"""

from flask import request, g
from flask_restplus import Resource
from mangiato.api.restplus import API
from mangiato.constants import (API_VERSION, CODE_NOT_FOUND, RESPONSES_CATALOG,
                                CODE_FORBIDDEN, CODE_OK, CODE_INTERNAL_ERROR,
                                CODE_BAD_REQUEST, )
from mangiato.globals import AUTH
from mangiato.api.serializers import PROFILE_MODEL
from mangiato.api.business.profiles import (get_profile, update_profile,
                                            get_avatar, update_avatar)
from mangiato.api.parsers import UPLOAD_PARSER


PROFILE_NS = API.namespace(API_VERSION + 'users/<int:id_user>/profile',
                           description='Operations related to user profile')
AVATAR_NS = API.namespace(API_VERSION + 'users/<int:id_user>/profile/avatar',
                          description='Operations related user avatar')


@PROFILE_NS.route('/', strict_slashes=False, methods=['GET', 'PUT'])
class Profile(Resource):
    """
    Represent the module to manage requests to resource corresponding to
    endpoint users/<id_user>/profile
    """
    @staticmethod
    @API.response(CODE_NOT_FOUND, str(RESPONSES_CATALOG['no_user_server']))
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_resource']))
    @API.response(CODE_OK, 'Success', PROFILE_MODEL)
    @AUTH.login_required
    def get(id_user):
        """
        Respond to a get method for users/<id_user>/profile endpoint
        to get profile's data of user
        :param id_user: user id coming from url, define the user which the
        request will be done
        :type: int
        :return: profile user, in this case only maximum calories per day.
        HTTPS status code
        :rtype: tuple(json,int)
        """
        return get_profile(id_user, g.user)

    @staticmethod
    @API.response(CODE_NOT_FOUND, str(RESPONSES_CATALOG['no_user_server']))
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_other_user']))
    @API.response(CODE_OK, 'Success', PROFILE_MODEL)
    @AUTH.login_required
    @API.expect(PROFILE_MODEL, validate=True)
    def put(id_user):
        """
        Respond to a PUT method for users/<id_user>/profile endpoint
        to modified user's profile (maximum calories per day)
        :param id_user: username coming from url, define the user which the
        request will be done
        :type: int
        :return: maximum calories per day modified. HTTP status code
        :rtype: tuple(json, int)
        """
        return update_profile(id_user, request.json, g.user)


@AVATAR_NS.route('/', strict_slashes=False, methods=['GET', 'PUT'])
class Avatar(Resource):
    """
    Represent the module to manage requests to resource corresponding to
    endpoint users/<id_user>/profile/avatar
    """

    @staticmethod
    @API.response(CODE_NOT_FOUND, str(RESPONSES_CATALOG['no_user_server']))
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_resource']))
    @AUTH.login_required
    def get(id_user):
        """
        Respond to a get method for users/<id_user>/profile/avatar endpoint
        to get the avatar of user or profile image
        :param id_user: user id coming from url, define the user which the
        request will be done
        :type: int
        :return: An image corresponding with user avatar. By default the server
         generate an random avatar. HTTPS status code
        :rtype: image
        """
        return get_avatar(id_user, g.user)

    @staticmethod
    @API.response(CODE_INTERNAL_ERROR,
                  str(RESPONSES_CATALOG['internal_error']))
    @API.response(CODE_NOT_FOUND, str(RESPONSES_CATALOG['no_user_server']))
    @API.response(CODE_BAD_REQUEST, str(RESPONSES_CATALOG['no_file_found']))
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_other_user']))
    @API.response(CODE_OK,
                  str(RESPONSES_CATALOG['profile_image_changed']))
    @API.expect(UPLOAD_PARSER)
    @AUTH.login_required
    def put(id_user):
        """
        Respond to a PUT method for users/<id_user>/profile/avatar endpoint
        to modified user's profile image (avatar)
        :param id_user: username coming from url, define the user which the
        request will be done
        :type: int
        :return: A json message of successfully change profile image or error
        otherwise. HTTP status code
        :rtype: tuple(json, int)
        """
        return update_avatar(id_user, request.files, g.user)
