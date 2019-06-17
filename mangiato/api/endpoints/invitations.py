"""
This module contains classes and methods related to invitations to new users
to be registered in Mangiato API
"""

from flask import request, g
from flask_restplus import Resource
from mangiato.api.restplus import API
from mangiato.constants import (API_VERSION, CODE_CONFLICT, RESPONSES_CATALOG,
                                CODE_CREATED, CODE_FORBIDDEN, CODE_OK,
                                CODE_NOT_FOUND, CODE_NO_CONTENT)
from mangiato.globals import AUTH
from mangiato.api.serializers import (INVITATION_MODEL, PAGE_OF_INVITATIONS,
                                      INVITATION_MODEL_PATCH,
                                      USER_DESCRIPTION, NEW_INVITATION_MODEL)
from mangiato.api.business.invitations import (create_invitation,
                                               accept_invitation,
                                               complete_invitation,
                                               get_invitations,
                                               get_invitation,
                                               patch_invitation,
                                               delete_invitation)
from mangiato.api.parsers import PAGE_ARGUMENTS_INV

INVITATIONS_NS = API.namespace(API_VERSION + 'users/invitations',
                               description='Operations related invitations')
INVITATION_NS = API.namespace(API_VERSION +
                              'users/invitations/<int:id_invitation>',
                              description='Operations related an specific '
                                          'invitations')


@INVITATIONS_NS.route('/', strict_slashes=False, methods=['POST', 'GET'])
class Invitations(Resource):
    """
    Represent resource corresponding to endpoint /user/invitations
    """
    @staticmethod
    @API.response(CODE_CONFLICT,
                  str(RESPONSES_CATALOG['existing_invitation']) + '\n' +
                  str(RESPONSES_CATALOG['existing_user']))
    @API.response(CODE_CREATED, 'Success', INVITATION_MODEL)
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_resource']))
    @API.expect(NEW_INVITATION_MODEL, validate=True)
    @AUTH.login_required
    def post():
        """
        Respond to a POST method for /users/invitations endpoint to create a
        new invitation to register in Mangiato API register a new user
        :return: Response successful if the invitation was created successfully
        and the email sent.
        :rtype: tuple(json, int)
        """
        return create_invitation(request.json, g.user)

    @staticmethod
    @API.response(CODE_OK, 'User with role admin', PAGE_OF_INVITATIONS)
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_resource']))
    @AUTH.login_required
    @API.expect(PAGE_ARGUMENTS_INV, validate=True)
    def get():
        """
        Respond to a GET method for /users/invitations endpoint to get the
        list of invitations in the server.
        :return: Response the list of invitations in the server or error if
        the requester don't have permissions to access to resource
        :rtype: tuple(json, int)
        """
        return get_invitations(request, g.user)


@INVITATION_NS.route('/', strict_slashes=False, methods=['GET', 'PATCH',
                                                         'DELETE'])
class Invitation(Resource):
    """
    Represent resource corresponding to endpoint user/invitations/
    <int:id_invitation>
    """

    @staticmethod
    @API.response(CODE_NOT_FOUND, str(RESPONSES_CATALOG['no_user_server']))
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_update_resource']))
    @API.response(CODE_OK, 'User with role admin', INVITATION_MODEL)
    @AUTH.login_required
    def get(id_invitation):
        """
        Respond to a GET method for /users/invitations/<id_invitation>
        endpoint to get an specific invitation in the server.
        :param id_invitation: Invitation id to get
        :type: int
        :return: Response the list of invitations in the server or error if
        the requester don't have permissions to access to resource. HTTP
        status code
        :rtype: tuple(json, int)
        """
        return get_invitation(id_invitation, g.user)

    @staticmethod
    @API.response(CODE_NOT_FOUND,
                  str(RESPONSES_CATALOG['no_invitation_server']))
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_change_email_invitation']) + "\n" +
                  str(RESPONSES_CATALOG['no_permission_update_resource']))
    @API.response(CODE_OK, 'Success', INVITATION_MODEL)
    @AUTH.login_required
    @API.expect(INVITATION_MODEL_PATCH, validate=True)
    def patch(id_invitation):
        """
        Respond to a PATCH method for /users/invitations/<id_invitation>
        endpoint to update fields of invitation, in this case only status can
        be change.
        :param id_invitation: Invitation id to update status
        :ptype: int
        :return: Invitation updated and HTTP status code
        :rtype: tuple(json, int)
        """
        return patch_invitation(id_invitation, request.json, g.user)

    @staticmethod
    @API.response(CODE_NOT_FOUND,
                  str(RESPONSES_CATALOG['no_invitation_server']))
    @API.response(CODE_NO_CONTENT,
                  str(RESPONSES_CATALOG['invitation_deleted']))
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_delete_resource']))
    @AUTH.login_required
    def delete(id_invitation):
        """
        Respond to a DELETE method for /users/invitations/<id_invitation>
        endpoint to delete an invitation fields of invitation.
        :param id_invitation: Invitation id to delete
        :ptype: int
        :return: A message in a json is deleted was successfully done, error
        otherwise and HTTP status code
        :rtype: tuple(json, int)
        """
        return delete_invitation(id_invitation, g.user)


@INVITATIONS_NS.route('/<int:id_invitation>/<string:token>',
                      strict_slashes=False, methods=['GET', 'POST'])
class InvitationConfirmation(Resource):
    """
    Represent resource corresponding to endpoint user/invitations/
    <id_invitation>/<token_invitation> to accept invitations
    """

    @staticmethod
    @API.response(CODE_OK, "Form Rendered")
    @API.response(CODE_NOT_FOUND,
                  str(RESPONSES_CATALOG['no_invitation_link']) + "\n" +
                  str(RESPONSES_CATALOG['invalid_link']))
    def get(id_invitation, token):
        """
        Respond to a GET method for /users/invitations/<id_invitation>/
        <token_invitation> endpoint to accept an invitation
        :param id_invitation: Invitation id to accept
        :type: int
        :param token: Token representing information related to invitation
        :type: str
        :return: Return a rendered form where the user must fill fields to
        complete registration. HTTP code status
        :rtype: form rendered, int
        """
        return accept_invitation(request.base_url, id_invitation, token)

    @staticmethod
    @API.response(CODE_NOT_FOUND,
                  str(RESPONSES_CATALOG['no_invitation_link']) + "\n" +
                  str(RESPONSES_CATALOG['invalid_link']))
    @API.response(CODE_CREATED, "User Registered", USER_DESCRIPTION)
    def post(id_invitation, token):
        """
        Respond to a POST method for /users/invitations/<id_invitation>/
        <token_invitation> endpoint to submit data to accept an invitation to
        be registered in MANGIATO API
        :param id_invitation: Invitation id to accept
        :type: int
        :param token: Token representing information related to invitation
        :type: str
        :return: Return information about the new user registered after filled
        information of invitation. HTTP code status
        :rtype: tuple(json, int
        """
        return complete_invitation(request.base_url, id_invitation, token)
