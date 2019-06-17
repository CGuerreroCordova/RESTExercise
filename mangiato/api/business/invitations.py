"""
Provide the business logic for Mangiato API invitations. All functions related
to invitations: to determine how data can be created, stored, changed and
provided to users.
"""

from datetime import datetime
from flask import render_template, url_for, make_response
from flask_restplus import marshal
from flask_wtf import FlaskForm
from wtforms import validators, StringField, PasswordField, SubmitField
from mangiato.database import DB
from mangiato.database.models import User, Role, Profile, Invitation
from mangiato.constants import (COMMON_USER_ROLE, RESPONSES_CATALOG,
                                CODE_CREATED, CODE_CONFLICT, CODE_OK,
                                CODE_NOT_FOUND, ADMIN_ROLE,
                                CODE_FORBIDDEN, CODE_NO_CONTENT,
                                CODE_NOT_ACCEPTABLE, EMAIL_REGEX,
                                FIELDS_INVITATION, STATUS_INVITATION)
from mangiato.globals import get_roles_user
from mangiato.api.parsers import PAGE_ARGUMENTS_INV
from mangiato.api.serializers import (USER_DESCRIPTION,
                                      INVITATION_MODEL, PAGE_OF_INVITATIONS)
from mangiato.api.verification import (generate_confirmation_token,
                                       confirm_token, send_email)
from mangiato.api.filtering import process_query


class RegistrationForm(FlaskForm):
    """
    Represent the form of acceptation which the future users must fill fields
    necessaries to complete the registration. Define fields of the form to
    complete
    """
    first_name = StringField('First Name', [validators.Length(min=4, max=25),
                                            validators.DataRequired()])
    last_name = StringField('Last Name', [validators.Length(min=4, max=25),
                                          validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Register Now')


def create_invitation(data, user_input):
    """
    Create a new invitation in the server and store in database. Send the
    email of acceptation to future user
    :param data: Information about the new invitation (email)
    :type: json
    :param user_input: User who made the request
    :type: User Model
    :return: A message about the invitation was successfully created, or an
    error message if not success. HTTP status code
    :type: tuple(json,int)
    """
    roles = get_roles_user(user_input)
    if roles.intersection({ADMIN_ROLE}):
        email = data.get('email')
        if EMAIL_REGEX.match(email):
            user_in_db = User.query.filter(User.username == email).first()
            invitation_in_db = Invitation.query.filter(Invitation.email ==
                                                       email).first()
            if user_in_db:
                response = RESPONSES_CATALOG['existing_user']
                code = CODE_CONFLICT
            elif invitation_in_db:
                response = RESPONSES_CATALOG['existing_invitation']
                code = CODE_CONFLICT
            else:
                invitation = Invitation(email)
                DB.session.add(invitation)
                DB.session.commit()
                token_account_verification = \
                    generate_confirmation_token(invitation.email)
                acceptation_url = \
                    url_for('api.v1/users/invitations_invitation_confirmation',
                            id_invitation=invitation.id,
                            token=token_account_verification, _external=True)

                html = render_template('invitation.html',
                                       acceptation_url=acceptation_url)
                subject = "Mangiato: keeping track of your meals and calories"
                send_email(invitation.email, subject, html)
                response = marshal(invitation, INVITATION_MODEL)
                code = CODE_CREATED
        else:
            response = RESPONSES_CATALOG['no_format_email_invitation']
            code = CODE_NOT_ACCEPTABLE
    else:
        response = dict(RESPONSES_CATALOG['no_permission_resource'])
        response['error'] = response['error'].format(id_user=user_input.id)
        code = CODE_FORBIDDEN
    return response, code


def accept_invitation(base_url, id_invitation, token):
    """
    Create the form of acceptation and it render dynamically with data related
    to this user
    :param base_url: url base of the query. Needed to fill the form with
    information about the invitations
    :type: str
    :param id_invitation: invitation id accepted
    :type: int
    :param token: acceptance token. The token must be confirmed before render
    the form
    :type: str
    :return: A form to complete information required
    :type: form html
    """
    email = confirm_token(token)
    if email:
        invitation = Invitation.query.filter_by(email=email).first()
        if invitation and invitation.id == id_invitation:
            form = RegistrationForm()
            headers = {'Content-Type': 'text/html'}
            return make_response(render_template('accept.html',
                                                 url_accept=base_url,
                                                 form=form),
                                 CODE_OK, headers)
        response = RESPONSES_CATALOG['no_invitation_link']
        code = CODE_NOT_FOUND
    else:
        response = RESPONSES_CATALOG['invalid_link']
        code = CODE_NOT_FOUND
    return response, code


def complete_invitation(base_url, id_invitation, token):
    """
    Get information from the form completed, check validation and create new
    user.
    :param base_url: url base of the query. Needed to fill the form with
    information about the invitations
    :type: str
    :param id_invitation: invitation id accepted
    :type: int
    :param token: acceptance token. The token must be confirmed before render
    the form
    :type: str
    :return: The new user created
    :type: tuple(json, int)
    """
    email = confirm_token(token)
    if email:
        invitation = Invitation.query.filter_by(email=email).first()
        if invitation and invitation.id == id_invitation:
            form = RegistrationForm()
            form_validated = form.validate_on_submit()
            if form_validated:
                new_user = User(email, form.first_name.data,
                                form.last_name.data, form.password.data,
                                confirmed=True, confirmed_on=datetime.now())
                role_common_user = Role.query.filter(Role.name ==
                                                     COMMON_USER_ROLE).first()
                new_user.roles.append(role_common_user)
                profile = Profile(new_user)
                invitation.accept()
                DB.session.add(invitation)
                DB.session.add(new_user)
                DB.session.add(profile)
                DB.session.commit()
                response = marshal(new_user, USER_DESCRIPTION)
                code = CODE_CREATED
            else:
                headers = {'Content-Type': 'text/html'}
                return make_response(render_template(
                    'accept.html', url_accept=base_url, form=form),
                    CODE_OK, headers)
        else:
            response = RESPONSES_CATALOG['no_invitation_link']
            code = CODE_NOT_FOUND
    else:
        response = RESPONSES_CATALOG['invalid_link']
        code = CODE_NOT_FOUND
    return response, code


def get_invitations(request, user_input):
    """
    Retrieve the list of invitations made in the API by the administrators
    :param request: context information about the current request
    :type: LocalProxy
    :param user_input: User who made the request
    :type: User Model
    :return: list of invitations made by administrators on the Mangiato API
    :type: tuple(json, int)
    """
    roles = get_roles_user(user_input)
    if roles.intersection({ADMIN_ROLE}):
        args = PAGE_ARGUMENTS_INV.parse_args(request)
        page = args.get('page', 1)
        per_page = args.get('per_page', 10)
        sort = args.get('sort', 'id')
        if sort not in FIELDS_INVITATION:
            response = {'error': 'Non acceptable ordering: ' + sort}
            code = CODE_NOT_ACCEPTABLE
            return response, code
        search = args.get('search')
        filter_query = ""
        model = "Invitation"
        if search:
            query_string = process_query(model, search)
            filter_query = ".filter({})".format(query_string)
        string_filter = model + ".query.order_by(" + model + "." + sort + \
                        ")" + filter_query + ".paginate(page, per_page, " \
                                             "error_out=False)"
        invitation_pages = eval(string_filter)
        response = marshal(invitation_pages, PAGE_OF_INVITATIONS)
        code = CODE_OK
    else:
        response = dict(RESPONSES_CATALOG['no_permission_resource'])
        response['error'] = response['error'].format(id_user=user_input.id)
        code = CODE_FORBIDDEN
    return response, code


def get_invitation(id_invitation, user_input):
    """
    Retrieve an invitation performed by the server and stored in database
    :param id_invitation: invitation id to retrieve
    :type: int
    :param user_input: User who made the request
    :type: User Model
    :return: information about invitation requested if success, error
    otherwise. HTTP status code
    :type: tuple(json, int)
    """
    roles = get_roles_user(user_input)
    if roles.intersection({ADMIN_ROLE}):
        invitation = Invitation.query.filter(Invitation.id ==
                                             id_invitation).first()
        if not invitation:
            response = dict(RESPONSES_CATALOG['no_invitation_server'])
            response['error'] = \
                response['error'].format(id_invitation=id_invitation)
            code = CODE_NOT_FOUND
        else:
            response = marshal(invitation, INVITATION_MODEL)
            code = CODE_OK
    else:
        response = dict(RESPONSES_CATALOG['no_permission_resource'])
        response['error'] = response['error'].format(id_user=user_input.id)
        code = CODE_FORBIDDEN
    return response, code


def patch_invitation(id_invitation, data, user_input):
    """
    Update information of a invitation on database. In this case only the
    status of invitation can be change. Updating an email may cause conflicts
    in the server
    :param id_invitation: invitation id to update
    :type: int
    :param data: new status of invitation
    :type: json
    :param user_input: User who made the request
    :type: User Model
    :return: Invitation updated if success, error message otherwise. HTTP
    status code
    :type: tuple(json, int)
    """
    roles = get_roles_user(user_input)
    if roles.intersection({ADMIN_ROLE}):
        invitation = Invitation.query.filter(Invitation.id ==
                                             id_invitation).first()
        email = data.get('email')
        status = data.get('status')
        if not invitation:
            response = dict(RESPONSES_CATALOG['no_invitation_server'])
            response['error'] = \
                response['error'].format(id_invitation=id_invitation)
            code = CODE_NOT_FOUND
        elif email is not None and email != invitation.email:
            response = RESPONSES_CATALOG['no_change_email_invitation']
            code = CODE_FORBIDDEN
        elif status in STATUS_INVITATION:
            invitation.status = data.get('status')
            DB.session.add(invitation)
            DB.session.commit()
            response = marshal(invitation, INVITATION_MODEL)
            code = CODE_OK
        else:
            response = {'error': 'Possible values for status: pending, '
                                 'accepted. No available: ' + status}
            code = CODE_NOT_ACCEPTABLE
    else:
        response = dict(RESPONSES_CATALOG['no_permission_update_resource'])
        response['error'] = response['error'].format(id_user=user_input.id)
        code = CODE_FORBIDDEN
    return response, code


def delete_invitation(id_invitation, user_input):
    """
    Delete a invitation from database. The requester must have
    permission to perform deletion. Only admins cam manage invitations.
    :param id_invitation: invitation id to update
    :type: int
    :param user_input: User who made the request
    :type: User Model
    :return: An message of deletion confirmation. error message otherwise.
    HTTP status code
    :type: tuple(json, int)
    """
    roles = get_roles_user(user_input)
    if roles.intersection({ADMIN_ROLE}):
        invitation = Invitation.query.filter(Invitation.id ==
                                             id_invitation).first()
        if not invitation:
            response = dict(RESPONSES_CATALOG['no_invitation_server'])
            response['error'] = \
                response['error'].format(id_invitation=id_invitation)
            code = CODE_NOT_FOUND
        else:
            DB.session.delete(invitation)
            DB.session.commit()
            response = RESPONSES_CATALOG['invitation_deleted']
            code = CODE_NO_CONTENT
    else:
        response = dict(RESPONSES_CATALOG['no_permission_delete_resource'])
        response['error'] = response['error'].format(id_user=user_input.id)
        code = CODE_FORBIDDEN
    return response, code
