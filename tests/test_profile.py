import os
from tests.test_api import TestAPI
from tests.commons import *
from mangiato.constants import *


class TestProfile(TestAPI):

    def test_get_profile(self):

        id_user = self._create_and_confirm_user()

        # happy path
        rv, json_result = self.client_common.get(
            self.catalog['profile'].format(id_user), content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertDictEqual(json_result, profile)

        # no user in server
        rv, json_result = \
            self.client_admin.get(self.catalog['profile'].format(id_user +
                                                              str(1)),
                                  content_type=None)
        response_to_cmp = dict(RESPONSES_CATALOG['no_user_server'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user + str(1))
        self.assertTrue(rv.status_code == CODE_NOT_FOUND)
        self.assertDictEqual(json_result, response_to_cmp)

        # fail no permission
        admin_id = 1
        rv, json_result = self.client_common.get(
            self.catalog['profile'].format(admin_id), content_type=None)
        response_to_cmp = dict(RESPONSES_CATALOG['no_permission_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user)
        self.assertTrue(rv.status_code == CODE_FORBIDDEN )
        self.assertDictEqual(json_result, response_to_cmp)


    def test_update_profile(self):

        id_user = self._create_and_confirm_user()

        # happy path
        rv, json_result = self.client_common.put(
            self.catalog['profile'].format(id_user), profile_update)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertDictEqual(json_result, profile_update)

        # no user in server - client admin
        rv, json_result = \
            self.client_admin.put(self.catalog['profile']
                                  .format(id_user + str(1)), profile_update)
        response_to_cmp = dict(RESPONSES_CATALOG['no_user_server'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user + str(1))
        self.assertTrue(rv.status_code == CODE_NOT_FOUND)
        self.assertDictEqual(json_result, response_to_cmp)

        # no user in server - client manager
        rv, json_result = \
            self.client_manager.put(self.catalog['profile']
                                  .format(id_user + str(1)), profile_update)
        response_to_cmp = dict(RESPONSES_CATALOG['no_user_server'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user + str(1))
        self.assertTrue(rv.status_code == CODE_NOT_FOUND)
        self.assertDictEqual(json_result, response_to_cmp)


