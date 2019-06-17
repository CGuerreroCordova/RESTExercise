"""
Parse arguments for pagination
"""

from flask_restplus import reqparse
from werkzeug.datastructures import FileStorage


PAGE_ARGUMENTS_MEALS = reqparse.RequestParser()
PAGE_ARGUMENTS_MEALS.add_argument('page', type=int, required=False, default=1,
                                  help='Page number')
PAGE_ARGUMENTS_MEALS.add_argument('per_page', type=int, required=False,
                                  default=10, help='Results per page')
PAGE_ARGUMENTS_MEALS.add_argument('search', type=str, required=False,
                                  help='Query search')
PAGE_ARGUMENTS_MEALS.add_argument('sort', type=str, required=False,
                                  default='id', choices=('meal_id', 'date',
                                                         'time',
                                                         'description',
                                                         'calories'),
                                  help='Order elements')

PAGE_ARGUMENTS_USERS = reqparse.RequestParser()
PAGE_ARGUMENTS_USERS.add_argument('page', type=int, required=False, default=1,
                                  help='Page number')
PAGE_ARGUMENTS_USERS.add_argument('per_page', type=int, required=False,
                                  default=10, help='Results per page')
PAGE_ARGUMENTS_USERS.add_argument('search', type=str, required=False,
                                  help='Query search')
PAGE_ARGUMENTS_USERS.add_argument('sort', type=str, required=False,
                                  default='id', choices=('id','username',
                                                         'first_name',
                                                         'confirmed',
                                                         'confirmed_on',
                                                         'attempts_login',
                                                         'blocked'),
                                  help='Order elements')

PAGE_ARGUMENTS_INV = reqparse.RequestParser()
PAGE_ARGUMENTS_INV.add_argument('page', type=int, required=False, default=1,
                                  help='Page number')
PAGE_ARGUMENTS_INV.add_argument('per_page', type=int, required=False,
                                  default=10, help='Results per page')
PAGE_ARGUMENTS_INV.add_argument('search', type=str, required=False,
                                  help='Query search')
PAGE_ARGUMENTS_INV.add_argument('sort', type=str, required=False,
                                  default='id', choices=('id', 'email',
                                                         'status'),
                                  help='Order elements')


UPLOAD_PARSER = reqparse.RequestParser()
UPLOAD_PARSER.add_argument('file', location='files', type=FileStorage,
                           required=True)
