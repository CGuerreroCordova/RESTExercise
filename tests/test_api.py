import unittest
import tempfile
from flask import url_for
from mangiato.mangiato_api import initialize_app
from mangiato.globals import APP
from mangiato.constants import *
from mangiato.database import DB
from tests.commons import *
from tests.test_client import TestClient
from mangiato.api.verification import generate_confirmation_token


class TestAPI(unittest.TestCase):

    def setUp(self):
        self.APP = APP
        self.db_fd, self.APP.config['DATABASE'] = tempfile.mkstemp()
        initialize_app(self.APP, 'test_config.py')
        self.ctx = self.APP.app_context()
        self.ctx.push()
        self.client_common = TestClient(self.APP, NEW_USER['username'],
                                        NEW_USER['password'])
        self.client_admin = TestClient(self.APP, ADMIN_USERNAME,
                                       ADMIN_PASSWORD)
        self.client_manager = TestClient(self.APP, MANAGER_USERNAME,
                                         MANAGER_PASSWORD)
        self.catalog = self._create_catalog()

    def tearDown(self):
        DB.session.remove()
        DB.drop_all()
        self.ctx.pop()

    def _create_catalog(self):
        with self.APP.test_request_context():
            url_login = url_for('api.v1/login_login', _external=True,
                                _scheme='https')
            url_users = url_for('api.v1/users_users', _external=True,
                                _scheme='https')
            url_user = url_for('api.v1/users/<int:id_user>_user',
                               id_user=str(1),
                               _external=True, _scheme='https')
            url_invitation = url_for('api.v1/users/invitations/'
                                     '<int:id_invitation>_invitation',
                                     id_invitation=str(1),
                                     _external=True, _scheme='https')
            url_invitations = url_for('api.v1/users/invitations_invitations',
                                      _external=True, _scheme='https')
            url_profile = url_for('api.v1/users/<int:id_user>/profile_profile',
                                  id_user=str(1),
                                  _external=True, _scheme='https')
            url_avatar = url_for('api.v1/users/<int:id_user>/profile/'
                                 'avatar_avatar',
                                  id_user=str(1),
                                  _external=True, _scheme='https')
            url_meals = url_for('api.v1/users/<int:id_user>/meals_meals',
                                  id_user=str(1),
                                  _external=True, _scheme='https')
            url_meal = url_for('api.v1/users/<int:id_user>/meals/'
                               '<int:id_meal>_meal',
                               id_user=str(1), id_meal=str(1), _external=True,
                               _scheme='https')
            url_user = url_user.replace("/1/", "/{}/")
            url_profile = url_profile.replace("/1/", "/{}/")
            url_avatar = url_avatar.replace("/1/", "/{}/")
            url_meals = url_meals.replace("/1/", "/{}/")
            url_meal = url_meal.replace("/1/", "/{}/")
            url_invitation = url_invitation.replace("/1/", "/{}/")

            json_catalog = dict()
            json_catalog['users'] = url_users
            json_catalog['login'] = url_login[:-1]
            json_catalog['user'] = url_user
            json_catalog['profile'] = url_profile
            json_catalog['avatar'] = url_avatar
            json_catalog['meals'] = url_meals
            json_catalog['meal'] = url_meal
            json_catalog['invitations'] = url_invitations
            json_catalog['invitation'] = url_invitation
        return json_catalog

    def _add_links_to_response(self, response, id_user):

        response_confirmed = dict(response)

        response_confirmed['id_user'] = str(id_user)
        response_confirmed['response'] = response_confirmed['response'] \
            .format(id_user=str(id_user))

        response_confirmed['links']['url_profile']['link'] = \
            self.catalog['profile'].format(str(id_user))
        response_confirmed['links']['url_avatar']['link'] = \
            self.catalog['avatar'].format(str(id_user))
        response_confirmed['links']['url_meals']['link'] = \
            self.catalog['meals'].format(str(id_user))

        return response_confirmed

    def _create_and_confirm_user(self):
        self.client_common.post(self.catalog['users'], data=NEW_USER)
        token_verification = generate_confirmation_token(NEW_USER['username'])
        url_verification = self.catalog['users'] + "confirm/" + \
                           token_verification
        rv, json_user =self.client_common.get(url_verification,
                                              content_type=None)
        return json_user['id_user']
