"""
This module contains classes and methods related to meals posted by users
registered on Mangiato API
"""
from flask import request, g
from flask_restplus import Resource
from mangiato.api.restplus import API
from mangiato.api.business.meals import (create_meal, get_meals, get_meal,
                                         update_meal, patch_meal, delete_meal)
from mangiato.api.parsers import PAGE_ARGUMENTS_MEALS
from mangiato.api.serializers import (MEAL_API_MODEL, PAGE_OF_MEALS,
                                      MEAL_API_MODEL_PATCH, NEW_MEAL_API_MODEL)
from mangiato.constants import (API_VERSION, CODE_NOT_FOUND, CODE_FORBIDDEN,
                                CODE_CREATED, CODE_OK, CODE_NO_CONTENT,
                                CODE_NOT_ACCEPTABLE, RESPONSES_CATALOG)
from mangiato.globals import AUTH


MEALS_NS = API.namespace(API_VERSION + 'users/<int:id_user>/meals',
                         description='Operations related to meals')
MEAL_NS = API.namespace(API_VERSION + 'users/<int:id_user>/meals/'
                                      '<int:id_meal>',
                        description='Operations related to a specific meal')


@MEALS_NS.route('/', strict_slashes=False, methods=['POST', 'GET'])
class Meals(Resource):
    """
    Represent the module to manage requests to users/<id_user>/meals endpoint.
    """
    @staticmethod
    @API.response(CODE_NOT_FOUND, str(RESPONSES_CATALOG['no_user_server']))
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_update_resource']))
    @API.response(CODE_CREATED, 'Success', MEAL_API_MODEL)
    @AUTH.login_required
    @API.expect(NEW_MEAL_API_MODEL, validate=True)
    def post(id_user):
        """
        Respond to a POST method request for users/<id_user>/meals endpoint to
        post a new meal
        :param id_user: id user who wants to post the meal
        :type: int
        :return: Meal posted. HTTP status code.
        :type: tuple(json, int)
        """
        return create_meal(id_user, request.json, g.user)

    @staticmethod
    @API.response(CODE_NOT_FOUND, str(RESPONSES_CATALOG['no_user_server']))
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_resource']))
    @API.response(CODE_NOT_ACCEPTABLE,
                  str(RESPONSES_CATALOG['error_parse_query_values']) + "\n" +
                  str(RESPONSES_CATALOG['error_parse_query_fields']))
    @API.response(CODE_OK, 'Success', PAGE_OF_MEALS)
    @AUTH.login_required
    @API.expect(PAGE_ARGUMENTS_MEALS, validate=True)
    def get(id_user):
        """
        Respond to a get method for users/<id_user>/meals endpoint to get the
        list of meals posted by this user
        :param id_user: id user who wants the list of its meals posted
        :type: int
        :return: list of meals posted by the user with id <id_user>. HTTP
        status code
        :rtype: tuple(json, int)
        """

        return get_meals(id_user, request, g.user)


@MEAL_NS.route('/', strict_slashes=False, methods=['GET', 'PUT', 'PATCH',
                                                   'DELETE'])
class Meal(Resource):
    """
    Represent the module to manage requests to resource corresponding to
    endpoint users/<id_user>/meals/<id_meal> endpoint
    """

    @staticmethod
    @API.response(CODE_NOT_FOUND, str(RESPONSES_CATALOG['no_user_server']) +
                  "\n" + str(RESPONSES_CATALOG['no_meal_user']) + "\n" +
                  str(RESPONSES_CATALOG['no_meal_server']))
    @API.response(CODE_OK, 'Success', MEAL_API_MODEL)
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_resource']))
    @AUTH.login_required
    def get(id_user, id_meal):
        """
        Respond to a get method for users/<id_user>/meals/<id_meal> endpoint
        to get an specific meal posted by the user
        :param id_user: user id coming from url, define the user which the
        request will be done
        :type: int
        :param id_meal: id meal to get
        :type: int
        :return: meal corresponding with id_user and id meal or an error if
        that id_entry not correspond with the user
        :rtype: tuple(json,int)
        """
        return get_meal(id_user, id_meal, g.user)

    @staticmethod
    @API.response(CODE_NOT_FOUND, str(RESPONSES_CATALOG['no_user_server']) +
                  "\n" + str(RESPONSES_CATALOG['no_meal_user']) + "\n" +
                  str(RESPONSES_CATALOG['no_meal_server']))
    @API.response(CODE_OK, 'Success', MEAL_API_MODEL)
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_update_resource']))
    @AUTH.login_required
    @API.expect(NEW_MEAL_API_MODEL, validate=True)
    def put(id_user, id_meal):
        """
        Respond to a PUT method for users/<id_user>/meals/<id_meal> endpoint
        to modified an specific meal posted by the user
        :param id_user: username coming from url, define the user which the
        request will be done
        :type: int
        :param id_meal: id user who wants to post the meal
        :type: int
        :return: meal modified
        :rtype: tuple(json, int)
        """
        return update_meal(id_user, id_meal, request.json, g.user)

    @staticmethod
    @API.response(CODE_NOT_FOUND, str(RESPONSES_CATALOG['no_user_server']) +
                  "\n" + str(RESPONSES_CATALOG['no_meal_user']) + "\n" +
                  str(RESPONSES_CATALOG['no_meal_server']))
    @API.response(CODE_OK, 'Success', MEAL_API_MODEL)
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_update_resource']))
    @AUTH.login_required
    @API.expect(NEW_MEAL_API_MODEL, validate=True)
    def patch(id_user, id_meal):
        """
        Respond to a PATCH method for users/<id_user>/meals/<id_meal>
        endpoint to modify an specific entry posted by the user, in this
        case the user can modify some fields, not all necessary
        :param id_user: username coming from url, define the user which the
        request will be done
        :type: int
        :param id_meal: id meal to be modified
        :type: int
        :return: meal modified or error if the meal doesn't belong to the user.
         HTTP status code
        :rtype: tuple(json, int)
        """
        return patch_meal(id_user, id_meal, request.json, g.user)

    @staticmethod
    @API.response(CODE_NOT_FOUND, str(RESPONSES_CATALOG['no_user_server']) +
                  "\n" + str(RESPONSES_CATALOG['no_meal_user']) + "\n" +
                  str(RESPONSES_CATALOG['no_meal_server']))
    @API.response(CODE_NO_CONTENT, str(RESPONSES_CATALOG['meal_deleted']))
    @API.response(CODE_FORBIDDEN,
                  str(RESPONSES_CATALOG['no_permission_delete_resource']))
    @AUTH.login_required
    def delete(id_user, id_meal):
        """
        Respond to delete method for users/<id_user>/meals/<id_meal> endpoint.
        Delete a meal
        :param id_user: username coming from url, define the user which the
        delete action of meal will be done
        :type: int
        :param id_meal: id meal to be deleted
        :type: int
        :return: empty. HTTP status code
        :rtype: int
        """
        return delete_meal(id_user, id_meal, g.user)
