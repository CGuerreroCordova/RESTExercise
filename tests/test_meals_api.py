from tests.test_api import TestAPI
from tests.commons import *
from mangiato.constants import *


class TestMeals(TestAPI):

    def test_post_meal(self):
        id_user = self._create_and_confirm_user()
        # happy path
        rv, json_result = \
            self.client_common.post(self.catalog['meals'].format(id_user),
                                    data=new_meal)
        self.assertTrue(rv.status_code == CODE_CREATED)
        self.assertTrue(json_result['date'] == new_meal['date'])
        self.assertTrue(json_result['time'] == new_meal['time'])
        self.assertTrue(json_result['description'] == new_meal['description'])
        self.assertTrue(json_result['calories_less_expected'] == True)

        # no permission
        # common user
        rv, json_result = \
            self.client_common.post(self.catalog['meals'].format(id_user +
                                                                 str(1)),
                                    data=new_meal)
        response_to_cmp = dict(RESPONSES_CATALOG['no_permission_update_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user)

        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result, response_to_cmp)

        # no permission manager
        rv, json_result = \
            self.client_manager.post(self.catalog['meals'].format(id_user),
                                    data=new_meal)
        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=2)

        # admin user
        rv, json_result = \
            self.client_admin.post(self.catalog['meals'].format(id_user),
                                   data=new_meal)
        self.assertTrue(rv.status_code == CODE_CREATED)
        self.assertTrue(json_result['date'] == new_meal['date'])
        self.assertTrue(json_result['time'] == new_meal['time'])
        self.assertTrue(json_result['description'] == new_meal['description'])
        self.assertTrue(json_result['calories_less_expected'] == True)

        # no user in server
        rv, json_result = \
            self.client_admin.post(self.catalog['meals'].format(id_user +
                                                                 str(1)),
                                    data=new_meal)
        response_to_cmp = dict(RESPONSES_CATALOG['no_user_server'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user + str(1))

        self.assertTrue(rv.status_code == CODE_NOT_FOUND )
        self.assertDictEqual(json_result, response_to_cmp)

    def test_get_meals(self):

        id_user = self._create_and_confirm_user()

        # happy path common user
        self.client_common.post(self.catalog['meals'].format(id_user),
                                data=new_meal)
        self.client_common.post(self.catalog['meals'].format(id_user),
                                data=new_meal)
        self.client_common.post(self.catalog['meals'].format(id_user),
                                data=new_meal)
        self.client_common.post(self.catalog['meals'].format(id_user),
                                data=new_meal)
        rv, json_result = self.client_common.get(
            self.catalog['meals'].format(id_user), content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)
        for meal in json_result['items']:
            self.assertTrue(meal['date'] == new_meal['date'])
            self.assertTrue(meal['time'] == new_meal['time'])
            self.assertTrue(meal['description'] == new_meal['description'])
            self.assertTrue(meal['calories_less_expected'] == True)

        # no user in server
        rv, json_result = \
            self.client_admin.get(self.catalog['meals'].format(id_user +
                                                              str(1)),
                                  content_type=None)
        response_to_cmp = dict(RESPONSES_CATALOG['no_user_server'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user + str(1))
        self.assertTrue(rv.status_code == CODE_NOT_FOUND)
        self.assertDictEqual(json_result, response_to_cmp)

        # no permission from manager
        rv, json_result = \
            self.client_manager.get(self.catalog['meals'].format(id_user),
                                    content_type=None)
        response_to_cmp = dict(RESPONSES_CATALOG['no_permission_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=str(2))
        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result, response_to_cmp)

    def test_get_meal(self):
        id_user = self._create_and_confirm_user()
        # happy path
        rv, json_result = \
            self.client_common.post(self.catalog['meals'].format(id_user),
                                    data=new_meal)
        meal_id = json_result['meal_id']
        self.assertTrue(rv.status_code == CODE_CREATED)

        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, meal_id), content_type=None)
        self.assertTrue(json_result['date'] == new_meal['date'])
        self.assertTrue(json_result['time'] == new_meal['time'])
        self.assertTrue(json_result['description'] == new_meal['description'])
        self.assertTrue(json_result['calories_less_expected'] == True)

        # fail cases
        # no meal in server
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, meal_id + 1),
            content_type=None)
        response_to_cmp = dict(RESPONSES_CATALOG['no_meal_server'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_meal=meal_id + 1)
        self.assertTrue(rv.status_code == CODE_NOT_FOUND)
        self.assertDictEqual(json_result, response_to_cmp)

        # no user in server
        rv, json_result = \
            self.client_admin.get(self.catalog['meal'].format(id_user + str(1),
                                                              meal_id),
                                  content_type=None)
        response_to_cmp = dict(RESPONSES_CATALOG['no_user_server'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user + str(1))
        self.assertTrue(rv.status_code == CODE_NOT_FOUND)
        self.assertDictEqual(json_result, response_to_cmp)

        # no permission from manager
        rv, json_result = \
            self.client_manager.get(self.catalog['meal'].format(id_user,
                                                              meal_id),
                                  content_type=None)
        response_to_cmp = dict(RESPONSES_CATALOG['no_permission_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=str(2))
        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result, response_to_cmp)

    def test_put_meal(self):

        id_user = self._create_and_confirm_user()

        # happy path
        rv, json_result = \
            self.client_common.post(self.catalog['meals'].format(id_user),
                                    data=new_meal)
        self.assertTrue(rv.status_code == CODE_CREATED)

        meal_id = json_result['meal_id']
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, meal_id), content_type=None)

        self.assertTrue(json_result['date'] == new_meal['date'])
        self.assertTrue(json_result['time'] == new_meal['time'])
        self.assertTrue(json_result['description'] == new_meal['description'])
        self.assertTrue(json_result['calories_less_expected'] == True)

        rv, json_result = \
            self.client_common.put(self.catalog['meal'].format(id_user,
                                                               meal_id),
                                    data=meal_update)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertTrue(json_result['date'] == response_meal_updated_1['date'])
        self.assertTrue(json_result['time'] == response_meal_updated_1['time'])
        self.assertTrue(json_result['description'] ==
                        response_meal_updated_1['description'])
        self.assertTrue(json_result['calories_less_expected'] == True)

        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, meal_id), content_type=None)

        self.assertTrue(json_result['date'] == response_meal_updated_1['date'])
        self.assertTrue(json_result['time'] == response_meal_updated_1['time'])
        self.assertTrue(json_result['description'] == response_meal_updated_1[
            'description'])
        self.assertTrue(json_result['calories_less_expected'] == True)

        # common user tries to update a meal of another user_id
        rv, json_result = \
            self.client_common.put(self.catalog['meal'].format(id_user + str(1),
                                                              meal_id),
                                   data=meal_update)
        response_to_cmp = \
            dict(RESPONSES_CATALOG['no_permission_update_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user)
        self.assertTrue(rv.status_code == CODE_FORBIDDEN )
        self.assertDictEqual(json_result, response_to_cmp)

        # no user in server
        rv, json_result = \
            self.client_admin.put(self.catalog['meal'].format(id_user + str(1),
                                                              meal_id),
                                  data=meal_update)
        response_to_cmp = dict(RESPONSES_CATALOG['no_user_server'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user + str(1))
        self.assertTrue(rv.status_code == CODE_NOT_FOUND )
        self.assertDictEqual(json_result, response_to_cmp)

        # no meal in server
        rv, json_result = \
            self.client_common.put(self.catalog['meal'].format(id_user,
                                                               meal_id + 1),
                                  data=meal_update)

        response_to_cmp = dict(RESPONSES_CATALOG['no_meal_server'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_meal=meal_id + 1)
        self.assertTrue(rv.status_code == CODE_NOT_FOUND)
        self.assertDictEqual(json_result, response_to_cmp)

    def test_patch_meal(self):

        id_user = self._create_and_confirm_user()

        # happy path
        rv, json_result = \
            self.client_common.post(self.catalog['meals'].format(id_user),
                                    data=new_meal)
        self.assertTrue(rv.status_code == CODE_CREATED)

        meal_id = json_result['meal_id']
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, meal_id), content_type=None)

        self.assertTrue(json_result['date'] == new_meal['date'])
        self.assertTrue(json_result['time'] == new_meal['time'])
        self.assertTrue(json_result['description'] == new_meal['description'])
        self.assertTrue(json_result['calories_less_expected'] == True)

        rv, json_result = \
            self.client_common.patch(self.catalog['meal'].format(id_user,
                                                                 meal_id),
                                    data=meal_patch)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertTrue(json_result['date'] == meal_patch['date'])
        self.assertTrue(json_result['time'] == meal_patch['time'])
        self.assertTrue(json_result['description'] == new_meal['description'])

        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, meal_id), content_type=None)

        self.assertTrue(json_result['date'] == meal_patch['date'])
        self.assertTrue(json_result['time'] == meal_patch['time'])
        self.assertTrue(json_result['description'] == new_meal['description'])

        rv, json_result = \
            self.client_common.patch(self.catalog['meal'].format(id_user,
                                                                 meal_id),
                                     data=meal_patch_2)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertTrue(json_result['date'] == meal_patch['date'])
        self.assertTrue(json_result['time'] == meal_patch['time'])
        self.assertTrue(json_result['description'] == meal_patch_2['description'])

        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, meal_id), content_type=None)

        self.assertTrue(json_result['date'] == meal_patch['date'])
        self.assertTrue(json_result['time'] == meal_patch['time'])
        self.assertTrue(json_result['description'] ==
                        meal_patch_2['description'])

        # common user tries to update a meal of another user_id
        rv, json_result = \
            self.client_common.patch(self.catalog['meal'].format(id_user + str(1),
                                                              meal_id),
                                   data=meal_patch)
        response_to_cmp = \
            dict(RESPONSES_CATALOG['no_permission_update_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user)
        self.assertTrue(rv.status_code == CODE_FORBIDDEN )
        self.assertDictEqual(json_result, response_to_cmp)

        # no user in server
        rv, json_result = \
            self.client_admin.patch(self.catalog['meal'].format(id_user +
                                                                str(1),
                                                                meal_id),
                                  data=meal_patch)
        response_to_cmp = dict(RESPONSES_CATALOG['no_user_server'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user + str(1))
        self.assertTrue(rv.status_code == CODE_NOT_FOUND )
        self.assertDictEqual(json_result, response_to_cmp)

        # no meal in server
        rv, json_result = \
            self.client_common.patch(self.catalog['meal'].format(id_user,
                                                                 meal_id + 1),
                                  data=meal_patch)

        response_to_cmp = dict(RESPONSES_CATALOG['no_meal_server'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_meal=meal_id + 1)
        self.assertTrue(rv.status_code == CODE_NOT_FOUND)
        self.assertDictEqual(json_result, response_to_cmp)


    def test_delete_meal(self):

        id_user = self._create_and_confirm_user()

        rv, json_result = \
            self.client_common.post(self.catalog['meals'].format(id_user),
                                    data=new_meal)
        self.assertTrue(rv.status_code == CODE_CREATED)

        meal_id = json_result['meal_id']

        # happy path - client admin
        rv, json_result = \
            self.client_admin.delete(self.catalog['meal'].format(id_user,
                                                                 meal_id))
        self.assertTrue(rv.status_code == CODE_NO_CONTENT)
        self.assertDictEqual(json_result, RESPONSES_CATALOG['meal_deleted'])

        # fail - manager tries to delete meal
        rv, json_result = \
            self.client_manager.delete(self.catalog['meal'].format(id_user,
                                                                 meal_id))
        response_to_cmp = dict(
            RESPONSES_CATALOG['no_permission_delete_resource'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=2)
        self.assertTrue(rv.status_code == CODE_FORBIDDEN)
        self.assertDictEqual(json_result, response_to_cmp)

        # fail - no user
        rv, json_result = \
            self.client_admin.delete(self.catalog['meal'].format(id_user +
                                                                 str(1),
                                                                 meal_id))
        response_to_cmp = dict(RESPONSES_CATALOG['no_user_server'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_user=id_user + str(1))
        self.assertTrue(rv.status_code == CODE_NOT_FOUND)
        self.assertDictEqual(json_result, response_to_cmp)

        # fail - no meal
        rv, json_result = \
            self.client_admin.delete(self.catalog['meal'].format(id_user,
                                                                 meal_id + 1))
        response_to_cmp = dict(RESPONSES_CATALOG['no_meal_server'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(id_meal=meal_id + 1)
        self.assertTrue(rv.status_code == CODE_NOT_FOUND)
        self.assertDictEqual(json_result, response_to_cmp)


    def test_get_meals_with_filters(self):

        id_user = self._create_and_confirm_user()

        # happy path common user
        self.client_common.post(self.catalog['meals'].format(id_user),
                                data=MEAL_1)
        self.client_common.post(self.catalog['meals'].format(id_user),
                                data=MEAL_2)
        self.client_common.post(self.catalog['meals'].format(id_user),
                                data=MEAL_3)
        self.client_common.post(self.catalog['meals'].format(id_user),
                                data=MEAL_4)
        self.client_common.post(self.catalog['meals'].format(id_user),
                                data=MEAL_5)
        self.client_common.post(self.catalog['meals'].format(id_user),
                                data=MEAL_6)
        self.client_common.post(self.catalog['meals'].format(id_user),
                                data=MEAL_7)
        self.client_common.post(self.catalog['meals'].format(id_user),
                                data=MEAL_8)
        self.client_common.post(self.catalog['meals'].format(id_user),
                                data=MEAL_9)
        list_of_results = list()
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 1), content_type=None)
        list_of_results.append(json_result)
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 4), content_type=None)
        list_of_results.append(json_result)
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 7), content_type=None)
        list_of_results.append(json_result)
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 8), content_type=None)
        list_of_results.append(json_result)
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 9), content_type=None)
        list_of_results.append(json_result)
        # must return 1,4,7,8,9
        query = "?search=time le '10:00:00' or description eq 'elephant'"
        rv, json_result = self.client_common.get(
            self.catalog['meals'].format(id_user) + query, content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)

        self.assertTrue(len(json_result['items']), 5)
        for meal in json_result['items']:
            self.assertIn(meal, list_of_results)


        # must return 1, 4, 5, 7, 9
        query = "?search=((time lt '10:00:00') OR (description eq 'elephant' " \
                "and time gt '21:05:00')) or ((description eq 'rice' and date " \
                "eq '2019-02-02') or ((description eq 'rice') AND date eq " \
                "'2019-02-01'))"

        list_of_results = list()
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 1), content_type=None)
        list_of_results.append(json_result)
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 4), content_type=None)
        list_of_results.append(json_result)
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 5), content_type=None)
        list_of_results.append(json_result)
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 7), content_type=None)
        list_of_results.append(json_result)
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 9), content_type=None)
        list_of_results.append(json_result)

        rv, json_result = self.client_common.get(
            self.catalog['meals'].format(id_user) + query, content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertEqual(len(json_result['items']), 5)
        for meal in json_result['items']:
            self.assertIn(meal, list_of_results)

        # must return empty
        query = "?search=(date eq '2016-05-01') AND ((calories gt 20) OR " \
                "(calories lt 10))"
        list_of_results = list()
        rv, json_result = self.client_common.get(
            self.catalog['meals'].format(id_user) + query, content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertEqual(len(json_result['items']), 0)
        for meal in json_result['items']:
            self.assertIn(meal, list_of_results)

        # happy path must return 1,3
        query = "?search=(date eq '2019-02-01') AND ((calories gt '1000') OR " \
                "(calories lt '750'))"
        list_of_results = list()

        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 1), content_type=None)
        list_of_results.append(json_result)
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 3), content_type=None)
        list_of_results.append(json_result)

        rv, json_result = self.client_common.get(
            self.catalog['meals'].format(id_user) + query, content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertEqual(len(json_result['items']), 2)
        for meal in json_result['items']:
            self.assertIn(meal, list_of_results)

        # happy path and, or and operator together values (no fields)
        # checking parenthesis and operator precedence
        # happy path must return 1,3, 4,5,6,7
        query = "?search=(date eq '2019-02-01') AND (calories gt '1000') OR " \
                "(calories lt 750)"
        list_of_results = list()
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 1), content_type=None)
        list_of_results.append(json_result)
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 3), content_type=None)
        list_of_results.append(json_result)
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 4), content_type=None)
        list_of_results.append(json_result)
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 5), content_type=None)
        list_of_results.append(json_result)
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 6), content_type=None)
        list_of_results.append(json_result)
        rv, json_result = self.client_common.get(
            self.catalog['meal'].format(id_user, 7), content_type=None)
        list_of_results.append(json_result)

        rv, json_result = self.client_common.get(
            self.catalog['meals'].format(id_user) + query, content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertEqual(len(json_result['items']), 6)
        for meal in json_result['items']:
            self.assertIn(meal, list_of_results)

        # fail - typing error in field calories
        query = "?search=(date eq '2019-02-01') AND ((calries gt '1000') OR " \
                "(calories lt '750'))"
        rv, json_result = self.client_common.get(
            self.catalog['meals'].format(id_user) + query, content_type=None)

        self.assertTrue(rv.status_code == CODE_NOT_ACCEPTABLE)
        response_to_cmp = dict(RESPONSES_CATALOG['error_parse_query_fields'])
        response_to_cmp['error'] = \
            response_to_cmp['error'].format(field_error=ERROR_QUERY_FIELDS)
        self.assertDictEqual(json_result, response_to_cmp)

        # fail - no quotes for values - rice without quotes
        query = "?search=((time lt '10:00:00') OR (description eq 'elephant' " \
                "and time gt '21:05:00')) or ((description eq 'rice' and date " \
                "eq '2019-02-02') or ((description eq rice and eggs) AND date eq " \
                "'2019-02-01'))"
        rv, json_result = self.client_common.get(
            self.catalog['meals'].format(id_user) + query, content_type=None)

        self.assertTrue(rv.status_code == CODE_NOT_ACCEPTABLE)
        self.assertDictEqual(json_result,
                             RESPONSES_CATALOG['error_parse_query_values'])


    def test_get_meals_pagination_sorting(self):

        id_user = self._create_and_confirm_user()
        self._post_bulk_meals(id_user)

        # happy path - normal result 10 result
        query = ""
        rv, json_result = self.client_common.get(
            self.catalog['meals'].format(id_user) + query, content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertTrue(len(json_result['items']), 10)
        self.assertTrue(json_result['items'][0]['description']=='meat')
        self.assertTrue(json_result['items'][0]['date'] == '2018-07-01')
        self.assertTrue(json_result['items'][0]['time'] == '10:01:45')
        self.assertTrue(json_result['page'] == 1)
        self.assertTrue(json_result['pages'] == 2)
        self.assertTrue(json_result['per_page'] == 10)
        self.assertTrue(json_result['total'] == 13)

        # happy path - normal result 3 results page 1
        query = "?per_page=3&page=1"
        rv, json_result = self.client_common.get(
            self.catalog['meals'].format(id_user) + query, content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertTrue(len(json_result['items']), 3)
        self.assertTrue(json_result['items'][0]['description'] == 'meat')
        self.assertTrue(json_result['items'][0]['date'] == '2018-07-01')
        self.assertTrue(json_result['items'][0]['time'] == '10:01:45')
        self.assertTrue(json_result['page'] == 1)
        self.assertTrue(json_result['pages'] == 5)
        self.assertTrue(json_result['per_page'] == 3)
        self.assertTrue(json_result['total'] == 13)

        # happy path - normal result 4 results page 3
        query = "?per_page=4&page=3"
        rv, json_result = self.client_common.get(
            self.catalog['meals'].format(id_user) + query, content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertTrue(len(json_result['items']), 4)
        self.assertTrue(json_result['items'][0]['description'] == 'banana')
        self.assertTrue(json_result['items'][0]['date'] == '2018-07-09')
        self.assertTrue(json_result['items'][0]['time'] == '10:09:45')
        self.assertTrue(json_result['page'] == 3)
        self.assertTrue(json_result['pages'] == 4)
        self.assertTrue(json_result['per_page'] == 4)
        self.assertTrue(json_result['total'] == 13)

        # happy path sort by description
        query = "?sort=description"
        rv, json_result = self.client_common.get(
            self.catalog['meals'].format(id_user) + query, content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertTrue(len(json_result['items']), 10)
        self.assertTrue(json_result['items'][0]['description'] == 'apple')
        self.assertTrue(json_result['items'][0]['date'] == '2018-07-06')
        self.assertTrue(json_result['items'][0]['time'] == '10:06:45')
        self.assertTrue(json_result['page'] == 1)
        self.assertTrue(json_result['pages'] == 2)
        self.assertTrue(json_result['per_page'] == 10)
        self.assertTrue(json_result['total'] == 13)

        # happy path sort by description and pagination
        query = "?sort=description&per_page=4&page=3"
        rv, json_result = self.client_common.get(
            self.catalog['meals'].format(id_user) + query, content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertTrue(len(json_result['items']), 4)
        self.assertTrue(json_result['items'][0]['description'] == 'pizza')
        self.assertTrue(json_result['items'][0]['date'] == '2018-07-12')
        self.assertTrue(json_result['items'][0]['time'] == '10:12:45')
        self.assertTrue(json_result['page'] == 3)
        self.assertTrue(json_result['pages'] == 4)
        self.assertTrue(json_result['per_page'] == 4)
        self.assertTrue(json_result['total'] == 13)

        # happy path sort by description and pagination, and filtering
        query = "?sort=description&per_page=4&page=2&search=date lt " \
                "'2018-07-03' or time ge '10:11:01' or description eq 'apple'"
        rv, json_result = self.client_common.get(
            self.catalog['meals'].format(id_user) + query, content_type=None)
        self.assertTrue(rv.status_code == CODE_OK)
        self.assertTrue(len(json_result['items']), 1)
        self.assertTrue(json_result['items'][0]['description'] == 'rice')
        self.assertTrue(json_result['items'][0]['date'] == '2018-07-02')
        self.assertTrue(json_result['items'][0]['time'] == '10:02:45')
        self.assertTrue(json_result['page'] == 2)
        self.assertTrue(json_result['pages'] == 2)
        self.assertTrue(json_result['per_page'] == 4)
        self.assertTrue(json_result['total'] == 6)

        # fail error in sort field
        query = "?sort=descrtion"
        rv, json_result = self.client_common.get(
            self.catalog['meals'].format(id_user) + query, content_type=None)
        response_to_cmp = dict(RESPONSES_CATALOG['error_sort'])
        response_to_cmp['sort'] = response_to_cmp['sort'].format('descrtion')
        self.assertTrue(rv.status_code == CODE_BAD_REQUEST)
        self.assertTrue(json_result['errors'] == response_to_cmp)

    def _post_bulk_meals(self, id_user):

        for meal_index in range(1, len(MEALS) + 1):
            number_variable = str(meal_index)
            if meal_index < 10:
                number_variable = '0' + number_variable
            meal_to_post = {
                'date': '2018-07-{}'.format(number_variable),
                'time': '10:{}:45'.format(number_variable),
                'description': MEALS[meal_index-1]
            }

            rv, json_result = \
                self.client_common.post(self.catalog['meals'].format(id_user),
                                        data=meal_to_post)
            self.assertTrue(rv.status_code == CODE_CREATED)
