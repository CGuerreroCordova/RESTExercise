"""
Constants useful for all the server
"""

import re
EMAIL_REGEX = re.compile(r'\S+@\S+\.\S+')
SORT_REGEX = re.compile(r'\w')

# SSL
CERTIFICATE_FILE = "mangiato/cert.pem"
KEY_CERTIFICATE_FILE = "mangiato/key.pem"
API_VERSION = "v1/"

# HTTP CODES
CODE_OK = 200
CODE_CREATED = 201
CODE_NO_CONTENT = 204
CODE_BAD_REQUEST = 400
CODE_UNAUTHORIZED = 401
CODE_FORBIDDEN = 403
CODE_NOT_FOUND = 404
CODE_METHOD_NOT_ALLOWED = 405
CODE_NOT_ACCEPTABLE = 406
CODE_CONFLICT = 409
CODE_INTERNAL_ERROR = 500

LIMITS_ATTEMPTS_LOGIN = 3

# ROLES
ADMIN_ROLE = 'admin'
MANAGER_ROLE = 'manager'
COMMON_USER_ROLE = 'common_user'

# QUERY CALORIES
ID_NUTRITIONIX = 'bed6db0c'
KEYS_NUTRITIONIX = 'a789b367b4511edcc31dca6b7a27fa27'
NUTRI_URL = 'https://api.nutritionix.com/v1_1/search/{meal}?results=0:5&' \
            'fields=nf_calories&appId={id}&appKey={key}'

AVERAGE_CALORIES_PER_DAY = 2250

# AVATARS
SMALL_SIZE_AVATAR = 36
MEDIUM_SIZE_AVATAR = 72
LARGE_SIZE_AVATAR = 180

ALLOWED_EXTENSIONS_AVATAR = ['img', 'jpeg', 'jpg', 'png']

# INVITATION STATUS
PENDING = 'pending'
ACCEPTED = 'accepted'

RESPONSES_CATALOG = dict()
# Responses
RESPONSES_CATALOG['mail_sent'] = \
    {'response': 'A confirmation email has been sent.'}
RESPONSES_CATALOG['confirmed'] = \
    {'id_user' : '{id_user}',
     'response': 'You have confirmed your account. Your user id is: {id_user} '
                 '. Now you can login on the Mangiato API.',
     'links': {
         'url_meals':{'description': "List of stored meals.",
                      'link': '{url_meals}'},
         'url_profile': {'description': "URL to get and update maximum "
                                        "calories per day",
                         'link': '{url_profile}'},
         'url_avatar': {'description': "URL to get and update your profile "
                                       "picture",
                        'link': '{url_avatar}'}
     }
     }
RESPONSES_CATALOG['already_confirmed'] = \
    {'response': 'Account already confirmed. Please login.',
     'links': {
         'url_meals':{'description': "List of stored meals.",
                      'link': '{url_meals}'},
         'url_profile': {'description': "URL to get and update maximum "
                                        "calories per day",
                         'link': '{url_profile}'},
         'url_avatar': {'description': "URL to get and update your profile "
                                       "picture",
                        'link': '{url_avatar}'}
     }
     }
RESPONSES_CATALOG['profile_image_changed'] = \
    {'response': 'Profile image changed successfully'}
RESPONSES_CATALOG['no_user_link'] = \
    {'error': 'The user corresponding to this link confirmation not exist '
              'anymore'}
RESPONSES_CATALOG['no_invitation_link'] = \
    {'error': 'The invitation corresponding to this link confirmation not '
              'exist anymore'}
RESPONSES_CATALOG['invalid_link'] = \
    {'error': 'The confirmation link is invalid or has expired.'}
RESPONSES_CATALOG['no_user_server'] = \
    {'error': "The user with id: {id_user} doesn't exist in the server"}
RESPONSES_CATALOG['no_meal_server'] = \
    {'error': "The meal with id: {id_meal} doesn't exist in the server"}
RESPONSES_CATALOG['no_invitation_server'] = \
    {'error': "The invitation with id: {id_invitation} doesn't exist in the "
              "server"}
RESPONSES_CATALOG['no_meal_user'] = \
    {'error': "The meal id provided: {id_meal} doesn't belong to the user "
              "with id: {id_user}"}
RESPONSES_CATALOG['no_permission_resource'] = \
    {"error": "The user with id: {id_user} does not have permissions to "
              "access this resource"}
RESPONSES_CATALOG['no_permission_update_resource'] = \
    {"error": "The user with id: {id_user} does not have permissions to "
              "update this resource"}
RESPONSES_CATALOG['no_permission_delete_resource'] = \
    {"error": "The user with id: {id_user} does not have permissions to "
              "delete this resource"}
RESPONSES_CATALOG['error_parse_query_values'] = \
    {'error': 'Error parsing query. Check correctness query syntax. Check '
              'parenthesis. Check if all strings values are quoted'}
RESPONSES_CATALOG['error_parse_query_fields'] = \
    {'error': 'Error parsing query. Check field name are correct. '
              '{field_error}'}
RESPONSES_CATALOG['no_permission_other_user'] = \
    {"error": "The user with id: {id_user} cannot update this resource "
              "corresponding to user with ig {id_user_2}."}
RESPONSES_CATALOG['no_file_found'] = {'error': 'No file found'}
RESPONSES_CATALOG['internal_error'] = \
    {'error': 'System error, unable to upload file'}
RESPONSES_CATALOG['existing_user'] = \
    {"error": "A user with this email is already registered on the server"}
RESPONSES_CATALOG['existing_invitation'] = \
    {"error": "An invitation to this email is already registered on the "
              "server"}
RESPONSES_CATALOG['user_deleted'] = {"response": "User successfully deleted"}
RESPONSES_CATALOG['meal_deleted'] = {"response": "Meal successfully deleted"}
RESPONSES_CATALOG['invitation_deleted'] = {"response": "Invitation successfully deleted"}
RESPONSES_CATALOG['no_change_email_invitation'] = \
    {"error": "Can't change invitation email"}
RESPONSES_CATALOG['unauthorized'] = \
    {'error': "Unauthorized access. Don't have permission to access to this "
              "resource"}
RESPONSES_CATALOG['unauthorized_password'] = \
    {'error': 'Unauthorized access. Invalid password. Remaining attempts: {}'}
RESPONSES_CATALOG['account_blocked'] = \
    {'error': 'Unauthorized access. This user has been blocked because it has '
              'reached the maximum number of failed login attempts: 3'}
RESPONSES_CATALOG['account_not_confirmed'] = \
    {"error": "Unauthorized access. This account has not been confirmed yet. "
              "Please check your email to activate. Remaining attempts: {}"}
RESPONSES_CATALOG['no_format_email'] = \
    {'error': "Error parsing input value email. Username must have a valid "
              "email format"}
RESPONSES_CATALOG['no_format_email_invitation'] = \
    {'error': "Error parsing input value email. Provide a valid email format "
              "for invitation"}

RESPONSES_CATALOG['internal_error_server'] = {'error': 'Internal error server'}
RESPONSES_CATALOG['error_sort'] = {'sort': "Order elements The value '{}' is "
                                           "not a valid choice for 'sort'."}
FIELDS_USERS = {'id', 'username', 'first_name', 'last_name', 'confirmed',
                'confirmed_on', 'attempts_login', 'blocked'}
FIELDS_MEALS = {'meal_id', 'date', 'time', 'description', 'calories',
                'calories_less_expected'}
FIELDS_INVITATION = {'id', 'email', 'status'}
STATUS_INVITATION = {'pending', 'accepted'}
