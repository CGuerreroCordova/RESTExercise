"""
Provide instantiation of elements useful for all the serve, authorization, api,
etc
"""

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_avatars import Avatars, Identicon
from mangiato.constants import ALLOWED_EXTENSIONS_AVATAR

APP = Flask(__name__)
AUTH = HTTPBasicAuth()
AVATARS = Avatars(APP)


def get_roles_user(user):
    """
    Giving a model user as input, return the set of role which the user belongs
    :param user: user to get roles
    :type: Model user
    :return: set of roles of user
    :type: set
    """
    roles = set()
    for role in user.roles:
        roles.add(role.name)
    return roles


def generate_avatar(username):
    """
    Generate avatars by default
    :param username: user name to generate file name of which avatar will be
    stored
    :type:
    :return:

    """
    avatar = Identicon()
    return avatar.generate(text=username)

def allowed_file(filename):
    """
    Decide if a filename is a valid image file having account its extension
    :param filename: file name
    :type: str
    :return: True if is a valid file, False otherwise
    :type:
    """
    return '.' in filename and \
        filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS_AVATAR
