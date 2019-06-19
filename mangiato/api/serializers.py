"""
Provide definition of models to input, validation and output of payload of API
"""
import re
from flask_restplus import fields
from mangiato.api.restplus import API

EMAIL_REGEX = re.compile(r'\S+@\S+\.\S+')


class TimeField(fields.Raw):
    """
    Field Class to format time fields in serializers
    """
    __schema_type__ = 'string'

    def format(self, value):
        """
        Apply "%H:%M:%S" format to value parameter of type: time
        :param value: parameter to apply the formatting
        :type: Time
        :return: Time value formatted to str "%H:%M:%S"
        :type: str
        """
        return value.strftime("%H:%M:%S")


NEW_USER_MODEL = API.model('New User', {
    'first_name': fields.String(required=True, description='First name '
                                                           'entered '
                                                           'by the user'),
    'last_name': fields.String(required=True, description='Last name entered '
                                                          'by the user'),
    'username': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description="User's password"),
})

ROLE_API_MODEL = API.model('Role', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of '
                                                    'a role'),
    'name': fields.String(required=True, description="Role's name"),
    'description': fields.String(required=False, description="Description of "
                                                             "role"),
}, mask='{name, description}')

PAGINATION = API.model('A page of results', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of '
                                           'results'),
    'total': fields.Integer(description='Total number of results'),
})

MEAL_API_MODEL = API.model('Meal', {
    'meal_id' : fields.Integer(readOnly=True, required=False,
                               description='The unique identifier of an '
                                           'entry'),
    'date' : fields.Date(required=True, description='Date when meal was '
                                                    'entered'),
    'time' : TimeField(required=True),
    'description' : fields.String(required=True,
                                  description='Meal description entered by '
                                              'the user'),
    'calories' : fields.Integer(required=False, description="Meal's calories",
                                min=0, max=50000),
    'calories_less_expected' :
        fields.Boolean(required=False,
                       description="Indicate if after entered this meals, the "
                                   "total for that day is less than expected "
                                   "number of calories per day"),
    'user_id' : fields.Integer(attribute='user.id'),
    'user': fields.String(attribute='user.username'),

}, mask='{meal_id, date, time, description, calories, calories_less_expected}')


NEW_MEAL_API_MODEL = API.model('New Meal', {
    'date': fields.Date(required=True, description='Date when meal was '
                                                    'entered'),
    'time': TimeField(required=True),
    'description': fields.String(required=True,
                                 description='Meal description entered by '
                                              'the user'),
    'calories': fields.Integer(required=False, description="Meal's calories",
                                min=0, max=50000),

}, mask='{date, time, description, calories}')


MEAL_API_MODEL_PATCH = API.model('Meal', {
    'meal_id' : fields.Integer(readOnly=True, required=False,
                               description='The unique identifier of an '
                                           'entry'),
    'date' : fields.Date(required=False, description='Date when meal was '
                                                     'entered'),
    'time' : TimeField(required=False),
    'description' : fields.String(required=False,
                                  description='Meal description entered by '
                                              'the user'),
    'calories' : fields.Integer(required=False, description="Meal's calories"),
    'calories_less_expected' :
        fields.Boolean(required=False,
                       description="Indicate if after entered this meals, the "
                                   "total for that day is less than expected "
                                   "number of calories per day"),
    'user_id' : fields.Integer(attribute='user.id'),
    'user': fields.String(attribute='user.username'),

}, mask='{meal_id, date, time, description, calories, calories_less_expected}')

PAGE_OF_MEALS = API.inherit('Page of meals', PAGINATION, {
    'items': fields.List(fields.Nested(MEAL_API_MODEL))
})

USER_DESCRIPTION = API.model('User Description', {
    'id': fields.Integer(readOnly=True, required=False,
                         description='The unique identifier of a user'),
    'username': fields.String(required=True, description='User email'),
    'first_name': fields.String(required=True, description='First name '
                                                           'entered by the '
                                                           'user'),
    'last_name': fields.String(required=True, description='Last name entered '
                                                          'by the user'),
    'confirmed': fields.Boolean(required=True, description='User registration '
                                                           'confirmed by '
                                                           'email'),
    'confirmed_on': fields.Date(required=True, description='Date of user '
                                                           'confirmation'),
    'attempts_login': fields.Integer(required=True, description='Number of '
                                                                'failed login '
                                                                'attempts'),
    'blocked': fields.Boolean(required=True, description='Account blocked '
                                                         'because exceeds '
                                                         'maximums login '
                                                         'attempts'),
    'roles': fields.List(fields.Nested(ROLE_API_MODEL), required=True),
}, mask='{id, username, first_name, last_name, confirmed, confirmed_on, '
        'attempts_login, blocked, roles}')

USER_DESCRIPTION_PUT = API.model('User Description PUT', {
    'username': fields.String(required=True, description='User email'),
    'first_name': fields.String(required=True, description='First name '
                                                           'entered by the '
                                                           'user'),
    'last_name': fields.String(required=True, description='Last name entered '
                                                          'by the user'),
    'confirmed': fields.Boolean(required=True, description='User registration '
                                                           'confirmed by '
                                                           'email'),
    'confirmed_on': fields.Date(required=True, description='Date of user '
                                                           'confirmation'),
    'attempts_login': fields.Integer(required=True, description='Number of '
                                                                'failed login '
                                                                'attempts'),
    'blocked': fields.Boolean(required=True, description='Account blocked '
                                                         'because exceeds '
                                                         'maximums login '
                                                         'attempts'),
    'roles': fields.List(fields.Nested(ROLE_API_MODEL)),
}, mask='{username, first_name, last_name, confirmed, confirmed_on, '
        'attempts_login, blocked, roles}')

USER_DESCRIPTION_PATCH = API.model('User Description patch', {
    'username': fields.String(description='User email'),
    'first_name': fields.String(description='First name of user'),
    'last_name': fields.String(description='Last name of user'),
    'confirmed': fields.Boolean(description='User registration confirmed by '
                                            'email'),
    'confirmed_on': fields.Date(description='Date of user confirmation'),
    'attempts_login': fields.Integer(description='Number of failed login '
                                                 'attempts'),
    'blocked': fields.Boolean(description='Account blocked because exceeds '
                                          'maximums login attempts'),
    'roles': fields.List(fields.Nested(ROLE_API_MODEL)),
}, mask='{id, username, first_name, last_name, confirmed, confirmed_on, '
        'attempts_login, blocked, roles}')

USER_WITH_ENTRIES = API.inherit('User with Entries', USER_DESCRIPTION, {
    'meals': fields.List(fields.Nested(MEAL_API_MODEL))
})

LOGIN_MODEL = API.model('Information about login', {
    'duration': fields.Integer(description="Duration (in seconds) of valid "
                                           "token to operate in api."),
    'token': fields.String(description="Token provided by login in api to "
                                       "operate with it."),
})

PROFILE_MODEL = API.model('Profile user.', {
    'maximum_calories': fields.Integer(description="Maximum calories "
                                                   "permitted per day for "
                                                   "each user",
                                       max=50000, min=0),
})

INVITATION_MODEL = API.model('Invitation to user', {
    'id': fields.Integer(readOnly=True, required=False,
                         description='The unique identifier of a user'),
    'email': fields.String(required=True, description='Mail for invitation'),
    'status': fields.String(required=False, description='Invitation status'),
})

NEW_INVITATION_MODEL = API.model('Invitation to user inputs', {
    'email': fields.String(required=True, description='Mail for invitation'),
})

INVITATION_MODEL_PATCH = API.model('Patch for invitations to user', {
    'email': fields.String(required=False, description='Mail for invitation'),
    'status': fields.String(required=False, description='Invitation status'),
})

PAGE_OF_INVITATIONS = API.inherit('Page of invitations', PAGINATION, {
    'items': fields.List(fields.Nested(INVITATION_MODEL))
})

PAGE_OF_USERS_MANAGER = API.inherit('Page of users manager', PAGINATION, {
    'items': fields.List(fields.Nested(USER_DESCRIPTION))
})

PAGE_OF_USERS_ADMIN = API.inherit('Page of users admin', PAGINATION, {
    'items': fields.List(fields.Nested(USER_WITH_ENTRIES))
})
