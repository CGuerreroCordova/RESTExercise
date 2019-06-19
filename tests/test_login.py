from tests.test_api import TestAPI
from tests.commons import *
from mangiato.constants import *
from tests.test_client import TestClient
from mangiato.api.verification import generate_confirmation_token


class TestLogin(TestAPI):

    def test_login(self):

        # happy path - login successful
        id_user = self._create_and_confirm_user()
        rv, json_result = \
            self.client_common.post(self.catalog['login'], data=None)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertTrue(json_result['duration'] == 600)
        self.assertTrue(json_result['token'] != None)

        # fail - try to login wrong password - Try 1
        attacker = TestClient(self.APP, NEW_USER['username'],
                              'fakepassword')

        rv, json_result = attacker.post(self.catalog['login'], data=None)

        response_to_cmp = dict(RESPONSES_CATALOG['unauthorized_password'])
        response_to_cmp['error'] = response_to_cmp['error'].format(2)
        self.assertTrue(rv.status_code == CODE_UNAUTHORIZED)
        self.assertTrue(json_result == response_to_cmp)

        # fail - try to login wrong password - Try 2
        rv, json_result = attacker.post(self.catalog['login'], data=None)
        response_to_cmp = dict(RESPONSES_CATALOG['unauthorized_password'])
        response_to_cmp['error'] = response_to_cmp['error'].format(1)
        self.assertTrue(rv.status_code == CODE_UNAUTHORIZED)
        self.assertTrue(json_result == response_to_cmp)

        # fail - try to login wrong password - Try 3 - Blocked
        rv, json_result = attacker.post(self.catalog['login'], data=None)
        self.assertTrue(rv.status_code == CODE_UNAUTHORIZED)
        self.assertTrue(json_result == RESPONSES_CATALOG['account_blocked'])

        # fail - More tries
        rv, json_result = attacker.post(self.catalog['login'], data=None)
        self.assertTrue(rv.status_code == CODE_UNAUTHORIZED)
        self.assertTrue(json_result == RESPONSES_CATALOG['account_blocked'])
        # fail - More tries
        rv, json_result = attacker.post(self.catalog['login'], data=None)
        self.assertTrue(rv.status_code == CODE_UNAUTHORIZED)
        self.assertTrue(json_result == RESPONSES_CATALOG['account_blocked'])

        # happy path - manager unblock
        rv, json_result = self.client_manager.patch(
            self.catalog['user'].format(id_user), UNBLOCK_USER)
        self.assertTrue(rv.status_code == CODE_OK)

        # happy path - user can login again
        rv, json_result = \
            self.client_common.post(self.catalog['login'], data=None)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertTrue(json_result['duration'] == 600)
        self.assertTrue(json_result['token'] != None)

        # try to login user not confirmed
        dummy_user = TestClient(self.APP, DUMMY_USER['username'],
                                DUMMY_USER['password'])
        dummy_user.post(self.catalog['users'], data=DUMMY_USER)

        # try without confirmation 1
        rv, json_result = dummy_user.post(self.catalog['login'], data=None)
        response_to_cmp = dict(RESPONSES_CATALOG['account_not_confirmed'])
        response_to_cmp['error'] = response_to_cmp['error'].format(2)
        self.assertTrue(rv.status_code == CODE_UNAUTHORIZED)
        self.assertTrue(json_result == response_to_cmp)

        # try without confirmation 3
        rv, json_result = dummy_user.post(self.catalog['login'], data=None)
        response_to_cmp = dict(RESPONSES_CATALOG['account_not_confirmed'])
        response_to_cmp['error'] = response_to_cmp['error'].format(1)
        self.assertTrue(rv.status_code == CODE_UNAUTHORIZED)
        self.assertTrue(json_result == response_to_cmp)

        # try without confirmation 3 - account blocked
        rv, json_result = dummy_user.post(self.catalog['login'], data=None)
        self.assertTrue(rv.status_code == CODE_UNAUTHORIZED)
        self.assertTrue(json_result == RESPONSES_CATALOG['account_blocked'])