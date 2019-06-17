import os
from tests.test_api import TestAPI
from tests.commons import *
from mangiato.constants import *
from mangiato.api.verification import generate_confirmation_token


class TestUsers(TestAPI):

    def test_post_user(self):

        # create new user non-existent
        rv, json_result = self.client_common.post(self.catalog['users'],
                                           data=NEW_USER)
        self.assertTrue(rv.status_code == CODE_CREATED)
        self.assertDictEqual(json_result, RESPONSES_CATALOG['mail_sent'])

        # create existing user
        rv, json_result = self.client_common.post(self.catalog['users'],
                                           data=NEW_USER)
        self.assertTrue(rv.status_code == CODE_CONFLICT)
        self.assertDictEqual(json_result, RESPONSES_CATALOG['existing_user'])

        # confirm account - users/confirm get
        token_verification = generate_confirmation_token(NEW_USER['username'])
        url_verification = self.catalog['users'] + "confirm/" + \
                           token_verification
        rv, json_result = self.client_common.get(url_verification,
                                                 content_type=None)
        id_user = json_result['id_user']

        response_confirmed = \
            self._add_links_to_response(RESPONSES_CATALOG['confirmed'],
                                        id_user)

        self.assertTrue(rv.status_code == CODE_OK)
        self.assertDictEqual(json_result, response_confirmed)

        # account already confirmed - users get
        rv, json_result = self.client_common.get(url_verification,
                                                 content_type=None)
        response_already_confirmed = \
            self._add_links_to_response(RESPONSES_CATALOG['already_confirmed'],
                                        id_user)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertDictEqual(json_result, response_already_confirmed)

        # wrong token
        rv, json_result = self.client_common.get(url_verification[:-1],
                                                 content_type=None)
        self.assertTrue(rv.status_code == CODE_NOT_FOUND)
        self.assertDictEqual(json_result,
                             RESPONSES_CATALOG['invalid_link'])

    def test_get_users(self):

        id_user = self._create_and_confirm_user()

        # get users as common_user
        rv, json_result = self.client_common.get(self.catalog['users'],
                                                 content_type=None)

        response_to_cmp = dict(RESPONSES_CATALOG['no_permission_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user)
        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result, response_to_cmp)

        # get users as admin
        rv, json_result = self.client_admin.get(self.catalog['users'],
                                                content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertDictEqual(json_result, USERS_LIST_ADMIN)

        # get users as manager
        rv, json_result = self.client_manager.get(self.catalog['users'],
                                                  content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertDictEqual(json_result, USERS_LIST_MANAGER)


    def test_get_user(self):
        id_user = self._create_and_confirm_user()

        # get user as common_user
        rv, json_result = self.client_common.get(
            self.catalog['user'].format(id_user),content_type=None)

        response_to_cmp = dict(RESPONSES_CATALOG['no_permission_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user)

        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result, response_to_cmp)

        # get user as admin
        rv, json_result = self.client_admin.get(
            self.catalog['user'].format(id_user), content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertDictEqual(json_result, USER_ADMIN)

        # get user as manager
        rv, json_result = self.client_manager.get(
            self.catalog['user'].format(id_user), content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertDictEqual(json_result, USER_MANAGER)

    def test_put_user(self):

        id_user = self._create_and_confirm_user()

        # happy path - client admin
        rv, json_result = self.client_admin.put(
            self.catalog['user'].format(id_user), UPDATE_USER)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertDictEqual(json_result, UPDATE_USER)

        # happy path - client manager
        rv, json_result = self.client_manager.put(
            self.catalog['user'].format(id_user), UPDATE_USER)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertDictEqual(json_result, UPDATE_USER)

        # fail - client admin - missing field
        rv, json_result = self.client_admin.put(
            self.catalog['user'].format(id_user),
            UPDATE_USER_FIRST_NAME_MISSING)
        self.assertTrue(rv.status_code == CODE_BAD_REQUEST)
        self.assertDictEqual(json_result, FIRST_NAME_MISSING_FAIL)

        # fail - common user
        rv, json_result = self.client_common.put(
            self.catalog['user'].format(id_user), UPDATE_USER)

        response_to_cmp = dict(
            RESPONSES_CATALOG['no_permission_update_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user)
        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result, response_to_cmp)

    def test_patch_user(self):

        id_user = self._create_and_confirm_user()

        # happy path - client admin
        rv, json_result = self.client_admin.patch(
            self.catalog['user'].format(id_user), PATCH_USER)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertDictEqual(json_result, PATCHED_USER)

        # happy path - client manager
        rv, json_result = self.client_manager.patch(
            self.catalog['user'].format(id_user), PATCH_USER)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertDictEqual(json_result, PATCHED_USER)

        # fail - common user
        rv, json_result = self.client_common.patch(
            self.catalog['user'].format(id_user), PATCH_USER)

        response_to_cmp = dict(
            RESPONSES_CATALOG['no_permission_update_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user)
        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result, response_to_cmp)

        # happy path - client manager
        rv, json_result = self.client_manager.patch(
            self.catalog['user'].format(id_user), PATCH_USER_2)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertDictEqual(json_result, PATCHED_USER_2)

    def test_delete_user(self):

        id_user = self._create_and_confirm_user()

        # happy path - client admin
        rv, json_result = \
            self.client_admin.delete(self.catalog['user'].format(id_user))
        self.assertTrue(rv.status_code == CODE_NO_CONTENT)
        self.assertDictEqual(json_result, RESPONSES_CATALOG['user_deleted'])

        id_user = self._create_and_confirm_user()

        # happy path - client manager
        rv, json_result = \
            self.client_manager.delete(self.catalog['user'].format(id_user))
        self.assertTrue(rv.status_code == CODE_NO_CONTENT)
        self.assertDictEqual(json_result, RESPONSES_CATALOG['user_deleted'])

        id_user = self._create_and_confirm_user()

        # fail - common client try delete manager
        rv, json_result = \
            self.client_common.delete(self.catalog['user'].format(2))
        response_to_cmp = dict(
            RESPONSES_CATALOG['no_permission_delete_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user)
        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result, response_to_cmp)

        # fail - no user
        rv, json_result = \
            self.client_admin.delete(self.catalog['user'].format(id_user +
                                                                 str(1)))
        response_to_cmp = dict(RESPONSES_CATALOG['no_user_server'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user + str(1))
        self.assertTrue(rv.status_code == CODE_NOT_FOUND)
        self.assertDictEqual(json_result, response_to_cmp)

        # fail - manager try to delete admin
        rv, json_result = \
            self.client_manager.delete(self.catalog['user'].format(1))
        response_to_cmp = dict(RESPONSES_CATALOG['no_permission_delete_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=2)
        self.assertTrue(rv.status_code == CODE_FORBIDDEN )
        self.assertDictEqual(json_result, response_to_cmp)
