"""
This module contains instance, initialization, error handler
"""
import os
import datetime
from flask import make_response, jsonify, g
from .api.endpoints.users import USERS_NS, USER_NS
from .api.endpoints.login import LOGIN_NS
from .api.endpoints.profiles import PROFILE_NS, AVATAR_NS
from .api.endpoints.meals import MEALS_NS, MEAL_NS
from .api.endpoints.invitations import INVITATIONS_NS, INVITATION_NS
from .api.restplus import API
from .database import DB, reset_database
from .database.models import User, Role, Profile
from .globals import AUTH, APP
from .constants import (CERTIFICATE_FILE, KEY_CERTIFICATE_FILE,
                        CODE_NOT_FOUND, CODE_UNAUTHORIZED, ADMIN_ROLE,
                        MANAGER_ROLE)


def initialize_app(flask_app, config):
    """
    Initialize API, add namespaces to it
    :param flask_app: Instance of flask app
    :type: Flask app
    :param config: Configuration file
    :type: str
    :return: None
    :type: void
    """
    flask_app.config.from_pyfile(config)

    API.add_namespace(LOGIN_NS)
    API.add_namespace(USERS_NS)
    API.add_namespace(USER_NS)
    API.add_namespace(MEALS_NS)
    API.add_namespace(MEAL_NS)
    API.add_namespace(PROFILE_NS)
    API.add_namespace(AVATAR_NS)
    API.add_namespace(INVITATIONS_NS)
    API.add_namespace(INVITATION_NS)
    DB.app = flask_app
    DB.init_app(flask_app)
    reset_database()

    from .api import BLUEPRINT
    API.init_app(BLUEPRINT)

    if 'api' not in flask_app.blueprints.keys():
        flask_app.register_blueprint(BLUEPRINT)
    add_users()


def run_app():
    """
    Run api
    :return: None
    :type: void
    """
    print(os.getcwd())
    APP.run(ssl_context=(CERTIFICATE_FILE, KEY_CERTIFICATE_FILE), debug=True,
            port='5002')


def add_users():
    with APP.test_request_context():
        DB.session.add(Role('admin', "CRUD all records and users."))
        DB.session.add(Role('manager', "CRUD only users."))
        DB.session.add(Role('common_user', "CRUD on their owned records."))
        admin_user = User(email='admin@admin.com',
                          password='admin',
                          first_name='Master',
                          last_name='OfScience',
                          confirmed=True,
                          confirmed_on=datetime.datetime.now()
                          )
        role_admin = Role.query.filter(Role.name == ADMIN_ROLE).first()
        admin_user.roles.append(role_admin)
        profile = Profile(admin_user)
        DB.session.add(profile)
        DB.session.add(admin_user)
        DB.session.commit()

        manager_user = User(email='manager@manager.com',
                            password='manager',
                            first_name='Golden',
                            last_name='Master',
                            confirmed=True,
                            confirmed_on=datetime.datetime.now()
                            )
        role_manager = Role.query.filter(Role.name == MANAGER_ROLE).first()
        manager_user.roles.append(role_manager)
        profile = Profile(manager_user)
        DB.session.add(profile)
        DB.session.add(manager_user)
        DB.session.commit()


@APP.errorhandler(CODE_NOT_FOUND)
def not_found(error):
    """
    Manage not found errors
    :param error: Error occurred
    :type: str
    :return: Response in json format of error. HTTP code status
    :type: json, int
    """
    return make_response(jsonify({'error': 'Not found' + str(error)}),
                         CODE_NOT_FOUND)


@AUTH.error_handler
def unauthorized():
    """
    Manage unauthorized errors
    :return:
    :return: Response in json format of error. HTTP code status
    :type: json, int
    """
    error = ""
    try:
        error = g.error
    except:
        pass
    return make_response(jsonify({'error': 'Unauthorized access. ' + error}),
                         CODE_UNAUTHORIZED)
