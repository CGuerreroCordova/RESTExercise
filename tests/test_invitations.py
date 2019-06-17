from tests.test_api import TestAPI
from tests.commons import *
from mangiato.constants import *
from mangiato.api.verification import generate_confirmation_token


class TestInvitations(TestAPI):

    def test_post_invitation(self):

        # happy path create new invitation non-existent
        rv, json_result = self.client_admin.post(self.catalog['invitations'],
                                                  data=NEW_INVITATION)
        self.assertTrue(rv.status_code == CODE_CREATED)
        self.assertDictEqual(json_result, INVITATION_CREATE)

        # create existing invitation
        rv, json_result = self.client_admin.post(self.catalog['invitations'],
                                                 data=NEW_INVITATION)
        self.assertTrue(rv.status_code == CODE_CONFLICT)
        self.assertDictEqual(json_result,
                             RESPONSES_CATALOG['existing_invitation'])

        # create invitation existing user
        id_user = self._create_and_confirm_user()

        rv, json_result = self.client_admin.post(self.catalog['invitations'],
                                                 data=NEW_INVITATION_2)
        self.assertTrue(rv.status_code == CODE_CONFLICT)
        self.assertDictEqual(json_result,
                             RESPONSES_CATALOG['existing_user'])

        # try to create invitation as common_user
        rv, json_result = self.client_common.post(self.catalog['invitations'],
                                                  data=NEW_INVITATION_2)

        response_to_cmp = dict(RESPONSES_CATALOG['no_permission_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user)
        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result, response_to_cmp)

        # try to create invitation as manager
        rv, json_result = self.client_manager.post(self.catalog['invitations'],
                                                   data=NEW_INVITATION_2)
        response_to_cmp = dict(RESPONSES_CATALOG['no_permission_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=str(2))
        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result, response_to_cmp)

    def test_get_invitations(self):

        rv, json_result = self.client_admin.post(self.catalog['invitations'],
                                                 data=NEW_INVITATION)
        self.assertTrue(rv.status_code == CODE_CREATED)
        invitation_id_1 = json_result['id']

        rv, json_result = self.client_admin.post(self.catalog['invitations'],
                                                 data=NEW_INVITATION_2)
        self.assertTrue(rv.status_code == CODE_CREATED)
        invitation_id_2 = json_result['id']

        # happy path
        rv, json_result = self.client_admin.get(self.catalog['invitations'],
                                                content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)
        for invitation in json_result['items']:
            self.assertTrue(invitation['status'] == 'pending')
            if invitation['id'] == 1:
                self.assertTrue(invitation['email'] == NEW_INVITATION['email'])
            else:
                self.assertTrue(invitation['email'] == NEW_INVITATION_2['email'])

        # no permission from common user
        id_user = self._create_and_confirm_user()

        rv, json_result = self.client_common.get(self.catalog['invitations'],
                                                 content_type=None)
        response_to_cmp = dict(RESPONSES_CATALOG['no_permission_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=str(id_user))
        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result, response_to_cmp)

        # no permission from manager
        rv, json_result = self.client_manager.get(self.catalog['invitations'],
                                                  content_type=None)
        response_to_cmp = dict(RESPONSES_CATALOG['no_permission_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=str(2))
        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result, response_to_cmp)

    def test_get_invitation(self):

        rv, json_result = self.client_admin.post(self.catalog['invitations'],
                                                 data=NEW_INVITATION)
        self.assertTrue(rv.status_code == CODE_CREATED)

        # happy path
        invitation_id = json_result['id']
        rv, json_result = self.client_admin.get(
            self.catalog['invitation'].format(invitation_id),
            content_type=None)

        self.assertTrue(rv.status_code == CODE_OK)
        self.assertTrue(json_result['id'] == INVITATION_CREATE['id'])
        self.assertTrue(json_result['email'] == INVITATION_CREATE['email'])
        self.assertTrue(json_result['status'] == INVITATION_CREATE['status'])

        # no permission from common user
        id_user = self._create_and_confirm_user()

        rv, json_result = \
            self.client_common.get(
                self.catalog['invitation'].format(invitation_id),
                content_type=None)
        response_to_cmp = dict(RESPONSES_CATALOG['no_permission_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=str(id_user))
        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result, response_to_cmp)

        # no permission from manager
        rv, json_result = \
            self.client_manager.get(self.catalog['invitation'].format(invitation_id),
                                    content_type=None)
        response_to_cmp = dict(RESPONSES_CATALOG['no_permission_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=str(2))
        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result, response_to_cmp)

        # no invitation in server

        rv, json_result = self.client_admin.get(
            self.catalog['invitation'].format(invitation_id + 1),
            content_type=None)

        response_to_cmp = dict(RESPONSES_CATALOG['no_invitation_server'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_invitation=invitation_id + 1)
        self.assertTrue(rv.status_code == CODE_NOT_FOUND )
        self.assertDictEqual(json_result, response_to_cmp)

    def test_invitations_confirmation(self):

        rv, json_result = self.client_admin.post(self.catalog['invitations'],
                                                 data=NEW_INVITATION)
        self.assertTrue(rv.status_code == CODE_CREATED)
        token_verification = generate_confirmation_token(NEW_INVITATION['email'])
        url_acceptation = self.catalog['invitations'] + \
                          str(json_result['id']) + "/" + token_verification
        # GET
        rv, json_result = \
            self.client_common.get(url_acceptation, content_type='text/html')
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertIn(ACCEPTANCE_PART, json_result)
        self.assertIn(ACCEPTANCE_PART_2, json_result)
        self.assertIn(url_acceptation.encode('utf-8'), json_result)

    def test_patch_invitation(self):

        rv, json_result = self.client_admin.post(self.catalog['invitations'],
                                                 data=NEW_INVITATION)
        self.assertTrue(rv.status_code == CODE_CREATED)
        self.assertDictEqual(json_result, INVITATION_CREATE)
        id_invitation = json_result['id']

        rv, json_result = \
            self.client_admin.patch(self.catalog['invitation'].format(id_invitation),
                                     data=PATCH_INVITATION)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertTrue(json_result['email'] == NEW_INVITATION['email'])
        self.assertTrue(json_result['status'] == PATCH_INVITATION['status'])

        rv, json_result = self.client_admin.get(
            self.catalog['invitation'].format(id_invitation),
            content_type=None)

        self.assertTrue(rv.status_code == CODE_OK)
        self.assertTrue(json_result['email'] == NEW_INVITATION['email'])
        self.assertTrue(json_result['status'] == PATCH_INVITATION['status'])

        # fail -  no invitation in server

        url_invitation = self.catalog['invitation'].format(id_invitation + 1)
        rv, json_result = \
            self.client_admin.patch(url_invitation, data=PATCH_INVITATION)

        response_to_cmp = dict(RESPONSES_CATALOG['no_invitation_server'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_invitation=id_invitation + 1)
        self.assertTrue(rv.status_code == CODE_NOT_FOUND)
        self.assertDictEqual(json_result, response_to_cmp)

        # fail - manager tries to patch invitation
        rv, json_result = \
            self.client_manager.patch(self.catalog['invitation'].format(id_invitation),
                                      data=PATCH_INVITATION)
        response_to_cmp = dict(
            RESPONSES_CATALOG['no_permission_update_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=2)
        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result, response_to_cmp)

        # fail tries to change email invitation

        rv, json_result = \
            self.client_admin.patch(
                self.catalog['invitation'].format(id_invitation),
                data=PATCH_INVITATION_EMAIL)
        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result,
                             RESPONSES_CATALOG['no_change_email_invitation'])


    def test_delete_invitation(self):

        rv, json_result = self.client_admin.post(self.catalog['invitations'],
                                                 data=NEW_INVITATION)
        self.assertTrue(rv.status_code == CODE_CREATED)
        self.assertDictEqual(json_result, INVITATION_CREATE)
        id_invitation = json_result['id']

        # happy path
        rv, json_result = \
            self.client_admin.delete(
                self.catalog['invitation'].format(id_invitation))
        self.assertTrue(rv.status_code == CODE_NO_CONTENT)
        self.assertDictEqual(json_result, RESPONSES_CATALOG['invitation_deleted'])

        # fail - no invitation server
        url_invitation = self.catalog['invitation'].format(id_invitation + 1)
        rv, json_result = \
            self.client_admin.delete(url_invitation)

        response_to_cmp = dict(RESPONSES_CATALOG['no_invitation_server'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_invitation=id_invitation + 1)
        self.assertTrue(rv.status_code == CODE_NOT_FOUND)
        self.assertDictEqual(json_result, response_to_cmp)

        # fail - manager tries to delete invitation
        rv, json_result = \
            self.client_manager.delete(
                self.catalog['invitation'].format(id_invitation))
        response_to_cmp = dict(
            RESPONSES_CATALOG['no_permission_delete_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=2)
        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result, response_to_cmp)

