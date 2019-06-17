"""
Provide the business logic for Mangiato API meals. All functions related
to meals: to determine how data can be created, stored, changed and
provided to users. Calculation of calories, error control, etc.
"""
import json
from datetime import datetime
from urllib.request import urlopen, HTTPError, URLError
from flask_restplus import marshal
from pyparsing import ParseException
from sqlalchemy import and_, or_
from mangiato.database import DB
from mangiato.database.models import User, Meal, Profile
from mangiato.constants import (RESPONSES_CATALOG, CODE_CREATED, CODE_OK,
                                CODE_NOT_FOUND, ADMIN_ROLE, CODE_FORBIDDEN,
                                CODE_NOT_ACCEPTABLE, NUTRI_URL, ID_NUTRITIONIX,
                                KEYS_NUTRITIONIX, CODE_NO_CONTENT,
                                FIELDS_MEALS)
from mangiato.globals import get_roles_user
from mangiato.api.parsers import PAGE_ARGUMENTS_MEALS
from mangiato.api.serializers import (MEAL_API_MODEL, PAGE_OF_MEALS)
from mangiato.api.filtering import process_query


def create_meal(id_user, data, user_input):
    """
    Create and store a new meal in database.
    :param id_user: User's id who the new meal will be assigned
    :type: int
    :param data: Information about the new meal to create
    :type: json
    :param user_input: User who made the request
    :type: User Model
    :return: The new meal created is success, error message otherwise. HTTP
    status
    :type: tuple(json, int)
    """
    roles = get_roles_user(user_input)
    if id_user == user_input.id or roles.intersection({ADMIN_ROLE}):
        user = User.query.filter(User.id == id_user).first()
        if not user:
            response = dict(RESPONSES_CATALOG['no_user_server'])
            response['error'] = response['error'].format(id_user=id_user)
            code = CODE_NOT_FOUND
        else:
            try:
                date_str = data.get('date')
                date = datetime.strptime(date_str, '%Y-%m-%d')
                time_in_datetime = datetime.strptime(data.get('time'),
                                                     '%H:%M:%S')
                time = datetime.time(time_in_datetime)
                description = data.get('description')
                calories = data.get('calories')
                if calories is None:
                    calories = get_calories_meal(description)
                profile = \
                    Profile.query.filter(Profile.user_id == id_user).first()
                maximum_calories_user = profile.maximum_calories
                less_calories = compute_calories_day(id_user, date_str, time,
                                                     calories,
                                                     maximum_calories_user)
                new_meal = Meal(date, time, description, calories, user)
                new_meal.calories_less_expected = less_calories
                DB.session.add(new_meal)
                DB.session.commit()
                response = marshal(new_meal, MEAL_API_MODEL)
                code = CODE_CREATED
            except (SyntaxError, ValueError) as error:
                response = {'error': "Error parsing input value: " +
                                     str(error)}
                code = CODE_NOT_ACCEPTABLE
    else:
        response = dict(RESPONSES_CATALOG['no_permission_update_resource'])
        response['error'] = response['error'].format(id_user=user_input.id)
        code = CODE_FORBIDDEN
    return response, code


def compute_calories_day(id_user, date, time, calories_now,
                         maximum_calories_user):
    """
    Compute calories and decide if the user has exceeded the maximum calories
    permitted for him. Compute calories per day. Compute calories per times
    lower than provided and compare with maximum_calories_user
    :param id_user: User id to which the meals belong
    :type: int
    :param date: Date to perform the calories calculation
    :type: date
    :param time: From midnight until this time the meals will be used to
    compute calories of day
    :type: time
    :param calories_now: Calories of the current meal
    :type: int
    :param maximum_calories_user: Maximum calories permitted for the current
    user
    :type: int
    :return: Decision if the calories computed execced the maximum calories
    permitted
    :type: tuple(json, int)
    """
    meals_day = Meal.query.filter(Meal.user_id == id_user,
                                  Meal.date == date,
                                  Meal.time <= time).all()
    if calories_now is not None:
        calories_day = [calories_now]
    else:
        calories_day = []
    for meal in meals_day:
        if meal.calories is not None:
            calories_day.append(meal.calories)

    less_calories = sum(calories_day) < maximum_calories_user
    return less_calories


def get_calories_meal(meal_input):
    """
    For meal get amount of calories from Nutritionix web site, make a query of
    top five items and perform an average of them
    :param meal_input: Meal to query the web site
    :type: str
    :return: Average calories of the top five items
    :type: int
    """
    try:
        filled_url = NUTRI_URL.format(id=ID_NUTRITIONIX, key=KEYS_NUTRITIONIX,
                                      meal=meal_input)
        nutrition_open = urlopen(filled_url)
        query_results = json.load(nutrition_open)
        meals_hits = query_results["hits"]
        calories_list = list()
        for meal in meals_hits:
            calories_list.append(meal['fields']['nf_calories'])
        if calories_list:
            calories_average = sum(calories_list) / len(calories_list)
        else:
            calories_average = None
    except HTTPError:
        calories_average = None
    except URLError:
        calories_average = None
    return calories_average


def get_meals(id_user, request, user_input):
    """
    Retrieve the list of meals corresponding to an user
    :param id_user: user id to retrieve list of meals
    :type: int
    :param request: context information about the current request
    :type: LocalProxy
    :param user_input: User who made the request
    :type: User Model
    :return: list of meals corresponding to the user id
    :type: tuple(json, int)
    """
    roles = get_roles_user(user_input)
    if id_user == user_input.id or roles.intersection({ADMIN_ROLE}):
        user = User.query.filter(User.id == id_user).first()
        if not user:
            response = dict(RESPONSES_CATALOG['no_user_server'])
            response['error'] = response['error'].format(id_user=id_user)
            code = CODE_NOT_FOUND
        else:
            args = PAGE_ARGUMENTS_MEALS.parse_args(request)
            page = args.get('page', 1)
            per_page = args.get('per_page', 10)
            sort = args.get('sort', 'id')
            if sort == 'id':
                sort = "meal_" + sort
            if sort not in FIELDS_MEALS:
                response = dict(RESPONSES_CATALOG['error_sort'])
                response['error'] = response['error'].format(sort)
                code = CODE_NOT_ACCEPTABLE
                return response, code
            search = args.get('search')
            filter_query = ""
            model = 'Meal'
            try:
                if search:
                    search = search.lower()
                    query_string = process_query(model, search)
                    filter_query = ".filter({})".format(query_string)
                string_filter = model + ".query.order_by(Meal." + sort + \
                                ").filter(" + model + \
                                ".user_id == user.id)" + filter_query + \
                                ".paginate(page, per_page, error_out=False)"
                entries_page = eval(string_filter)
                response = marshal(entries_page, PAGE_OF_MEALS)
                code = CODE_OK
            except ParseException:
                response = RESPONSES_CATALOG['error_parse_query_values']
                code = CODE_NOT_ACCEPTABLE
            except AttributeError as error:
                response = dict(RESPONSES_CATALOG['error_parse_query_fields'])
                response['error'] = response['error'].format(field_error=error)
                code = CODE_NOT_ACCEPTABLE
    else:
        response = dict(RESPONSES_CATALOG['no_permission_resource'])
        response['error'] = response['error'].format(id_user=user_input.id)
        code = CODE_FORBIDDEN
    return response, code


def get_meal(id_user, id_meal, user_input):
    """
    Retrieve a specific meal corresponding to an user with id <id_user>
    :param id_user: user id to retrieve the meal requested
    :type: int
    :param id_meal: meal id to get from server
    :type: int
    :param user_input: User who made the request
    :type: User Model
    :return: list of meals corresponding to the user id
    :type: tuple(json, int)
    """
    roles = get_roles_user(user_input)
    if id_user == user_input.id or roles.intersection({ADMIN_ROLE}):
        user = User.query.filter(User.id == id_user).first()
        meal = Meal.query.filter(Meal.meal_id == id_meal).first()
        if not user:
            response = dict(RESPONSES_CATALOG['no_user_server'])
            response['error'] = response['error'].format(id_user=id_user)
            code = CODE_NOT_FOUND
        elif not meal:
            response = dict(RESPONSES_CATALOG['no_meal_server'])
            response['error'] = response['error'].format(id_meal=id_meal)
            code = CODE_NOT_FOUND
        elif meal.user.id != id_user:
            response = dict(RESPONSES_CATALOG['no_meal_user'])
            response['error'] = response['error'].format(id_meal=id_meal,
                                                         id_user=id_user)
            code = CODE_NOT_FOUND
        else:
            response = marshal(meal, MEAL_API_MODEL)
            code = CODE_OK
    else:
        response = dict(RESPONSES_CATALOG['no_permission_resource'])
        response['error'] = response['error'].format(id_user=user_input.id)
        code = CODE_FORBIDDEN
    return response, code


def update_meal(id_user, id_meal, data, user_input):
    """
    Update information of a meal on database. All fields of meal are required.
    Having in account a modification of a meal impacts in de flag if the user
    reach maximum calories permitted per day, if the meal is modified or the
    date or time, this trigger the re-calculation of the flag for all meals in
    the day that the change impacts
    :param id_user: user id corresponding to user which the meal belongs
    :type: int
    :param id_meal: meal id to update
    :type: int
    :param data: new information to store of the meal
    :type: json
    :param user_input: User who made the request
    :type: User Model
    :return: Meal updated if success, error message otherwise. HTTP status code
    :type: tuple(json, int)
    """
    roles = get_roles_user(user_input)
    if id_user == user_input.id or roles.intersection({ADMIN_ROLE}):
        user = User.query.filter(User.id == id_user).first()
        meal = Meal.query.filter(Meal.meal_id == id_meal).first()
        if not user:
            response = dict(RESPONSES_CATALOG['no_user_server'])
            response['error'] = response['error'].format(id_user=id_user)
            code = CODE_NOT_FOUND
        elif not meal:
            response = dict(RESPONSES_CATALOG['no_meal_server'])
            response['error'] = response['error'].format(id_meal=id_meal)
            code = CODE_NOT_FOUND
        elif meal.user_id != id_user:
            response = dict(RESPONSES_CATALOG['no_meal_user'])
            response['error'] = response['error'].format(id_meal=id_meal,
                                                         id_user=id_user)
            code = CODE_NOT_FOUND
        else:
            try:
                old_date_meal = meal.date
                old_time_entry = meal.time
                date_entry = datetime.strptime(data.get('date'), '%Y-%m-%d')
                meal.date = date_entry
                time_in_datetime = datetime.strptime(data.get('time'),
                                                     '%H:%M:%S')
                meal.time = datetime.time(time_in_datetime)
                old_description = meal.description
                meal.description = data.get('description')
                meal.calories = data.get('calories')
                if old_description != meal.description or \
                        meal.calories is None:
                    meal.calories = get_calories_meal(meal.description)
                DB.session.add(meal)
                DB.session.commit()
                _recalculate_calories_less_expected(id_user, meal.date,
                                                    meal.time)
                if old_date_meal != meal.date:
                    _recalculate_calories_less_expected(id_user, old_date_meal,
                                                        old_time_entry)
                response = marshal(meal, MEAL_API_MODEL)
                code = CODE_OK
            except (SyntaxError, ValueError) as error:
                response = {'error': "Error parsing input value: " +
                                     str(error)}
                code = CODE_NOT_ACCEPTABLE
    else:
        response = dict(RESPONSES_CATALOG['no_permission_update_resource'])
        response['error'] = response['error'].format(id_user=user_input.id)
        code = CODE_FORBIDDEN
    return response, code


def _recalculate_calories_less_expected(id_user, date, time):
    """
    Perform a re-calculation of flag that indicates if the user exceed its
    maximum calories permitted per day. Perform the re-calculation for the
    date provided an for the time lower-equal than provided. All results are
    stored in database
    :param id_user: user which the meals affected by re-calculation belong
    :type: int
    :param date: date of re-calculation
    :type: date
    :param time: maximum time of re-calculation
    :type: time
    :return: Empty
    :type: void
    """
    meals_day = Meal.query.filter(Meal.user_id == id_user,
                                  Meal.date == date,
                                  Meal.time >= time).all()
    profile_user = Profile.query.filter(Profile.user_id == id_user).first()
    maximum_calories = profile_user.maximum_calories
    for meal in meals_day:
        less_calories = compute_calories_day(id_user, date, meal.time,
                                             meal.calories,
                                             maximum_calories)
        meal.calories_less_expected = less_calories
        DB.session.add(meal)
        DB.session.commit()


def patch_meal(id_user, id_meal, data, user_input):
    """
    Update some or all information of a meal on database. In this case not all
    fields of meal are required.
    Having in account a modification of a meal impacts in de flag if the user
    reach maximum calories permitted per day, if the meal is modified or the
    date or time, this trigger the re-calculation of the flag for all meals in
    the day that the change impacts
    :param id_user: user id corresponding to user which the meal belongs
    :type: int
    :param id_meal: meal id to update
    :type: int
    :param data: new information to store of the meal
    :type: json
    :param user_input: User who made the request
    :type: User Model
    :return: Meal updated if success, error message otherwise. HTTP status code
    :type: tuple(json, int)
    """
    roles = get_roles_user(user_input)
    if id_user == user_input.id or roles.intersection({ADMIN_ROLE}):
        user = User.query.filter(User.id == id_user).first()
        meal = Meal.query.filter(Meal.meal_id == id_meal).first()
        if not user:
            response = dict(RESPONSES_CATALOG['no_user_server'])
            response['error'] = response['error'].format(id_user=id_user)
            code = CODE_NOT_FOUND
        elif not meal:
            response = dict(RESPONSES_CATALOG['no_meal_server'])
            response['error'] = response['error'].format(id_meal=id_meal)
            code = CODE_NOT_FOUND
        elif meal.user_id != id_user:
            response = dict(RESPONSES_CATALOG['no_meal_user'])
            response['error'] = response['error'].format(id_meal=id_meal,
                                                         id_user=id_user)
            code = CODE_NOT_FOUND
        else:
            try:
                old_date_meal = meal.date
                old_time_entry = meal.time
                old_description_meal = meal.description
                if data.get('date') is not None:
                    meal.date = datetime.strptime(data.get('date'), '%Y-%m-%d')
                if data.get('time') is not None:
                    time_in_datetime = datetime.strptime(data.get('time'),
                                                         '%H:%M:%S')
                    meal.time = datetime.time(time_in_datetime)
                if data.get('description') is not None:
                    meal.description = data.get('description')
                if data.get('calories') is not None:
                    meal.calories = data.get('calories')
                if old_description_meal != meal.description or \
                        meal.description is None:
                    meal.calories = get_calories_meal(meal.description)
                DB.session.add(meal)
                DB.session.commit()
                _recalculate_calories_less_expected(id_user, meal.date,
                                                    meal.time)
                if old_date_meal != meal.date:
                    _recalculate_calories_less_expected(id_user, old_date_meal,
                                                        old_time_entry)
                response = marshal(meal, MEAL_API_MODEL)
                code = CODE_OK
            except (SyntaxError, ValueError) as error:
                response = {'error': "Error parsing input value: " +
                                     str(error)}
                code = CODE_NOT_ACCEPTABLE
    else:
        response = dict(RESPONSES_CATALOG['no_permission_update_resource'])
        response['error'] = response['error'].format(id_user=user_input.id)
        code = CODE_FORBIDDEN
    return response, code


def delete_meal(id_user, id_meal, user_input):
    """
    Delete a meal from database server. The requester must have
    permission to perform deletion. The meal must to belong it or must have
    admin permission. The deletion of a meal also trigger the recalculation of
    flag of maximum calories reached for that day
    :param id_user: user id which the meal belong
    :type: int
    :param id_meal: meal id to delete
    :type: int
    :param user_input: User who made the request
    :type: User Model
    :return: An message of deletion confirmation. error message otherwise.
    HTTP status code
    :type: tuple(json, int)
    """
    roles = get_roles_user(user_input)
    if id_user == user_input.id or roles.intersection({ADMIN_ROLE}):
        user = User.query.filter(User.id == id_user).first()
        meal = Meal.query.filter(Meal.meal_id == id_meal).first()
        if not user:
            response = dict(RESPONSES_CATALOG['no_user_server'])
            response['error'] = response['error'].format(id_user=id_user)
            code = CODE_NOT_FOUND
        elif not meal:
            response = dict(RESPONSES_CATALOG['no_meal_server'])
            response['error'] = response['error'].format(id_meal=id_meal)
            code = CODE_NOT_FOUND
        elif meal.user_id != id_user:
            response = dict(RESPONSES_CATALOG['no_meal_user'])
            response['error'] = response['error'].format(id_meal=id_meal,
                                                         id_user=id_user)
            code = CODE_NOT_FOUND
        else:
            date_meal = meal.date
            time_meal = meal.time
            DB.session.delete(meal)
            DB.session.commit()
            _recalculate_calories_less_expected(id_user, date_meal, time_meal)
            response = RESPONSES_CATALOG['meal_deleted']
            code = CODE_NO_CONTENT
    else:
        response = dict(RESPONSES_CATALOG['no_permission_delete_resource'])
        response['error'] = response['error'].format(id_user=user_input.id)
        code = CODE_FORBIDDEN
    return response, code
