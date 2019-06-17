"""
Provide the business logic for Mangiato API users profile. All functions
related to user profile: change data profile, change image profile
"""
import os
from PIL import Image
from flask import send_file
from flask_restplus import marshal
from sqlalchemy import and_, or_
from mangiato.database import DB
from mangiato.database.models import User, Profile
from mangiato.constants import (RESPONSES_CATALOG, CODE_OK, CODE_NOT_FOUND,
                                ADMIN_ROLE, MANAGER_ROLE, CODE_FORBIDDEN,
                                CODE_BAD_REQUEST, CODE_INTERNAL_ERROR,
                                SMALL_SIZE_AVATAR, MEDIUM_SIZE_AVATAR,
                                LARGE_SIZE_AVATAR)
from mangiato.globals import get_roles_user, APP, allowed_file
from mangiato.api.serializers import PROFILE_MODEL


def get_profile(id_user, user_input):
    """
    Retrieve the a user profile, in this case the profile only contains
    maximum calories permitted per day
    :param id_user: user id to retrieve the profile
    :type: int
    :param user_input: user id to which the profile belongs
    :type: User Model
    :return: user profile. HTTP status code
    :type: tuple(json, int)
    """
    roles = get_roles_user(user_input)
    if id_user == user_input.id or roles.intersection({ADMIN_ROLE,
                                                       MANAGER_ROLE}):
        user = User.query.filter(User.id == id_user).first()
        profile = Profile.query.filter(Profile.user_id == id_user).first()
        if not user:
            response = dict(RESPONSES_CATALOG['no_user_server'])
            response['error'] = response['error'].format(id_user=id_user)
            code = CODE_NOT_FOUND
        else:
            response = marshal(profile, PROFILE_MODEL)
            code = CODE_OK
    else:
        response = dict(RESPONSES_CATALOG['no_permission_resource'])
        response['error'] = response['error'].format(id_user=user_input.id)
        code = CODE_FORBIDDEN
    return response, code


def update_profile(id_user, data, user_input):
    """
    Update of an user profile. In this case only maximum calories per day can
    be modified
    :param id_user: user id corresponding to user to update profile
    :type: int
    :param data: new information to store in the profile
    :type: json
    :param user_input: User who made the request
    :type: User Model
    :return: Profile updated if success, error message otherwise. HTTP status
    code
    :type: tuple(json, int)
    """
    roles = get_roles_user(user_input)
    if id_user == user_input.id or roles.intersection({ADMIN_ROLE,
                                                       MANAGER_ROLE}):
        user = User.query.filter(User.id == id_user).first()
        profile = Profile.query.filter(Profile.user_id == id_user).first()
        if not user:
            response = dict(RESPONSES_CATALOG['no_user_server'])
            response['error'] = response['error'].format(id_user=id_user)
            code = CODE_NOT_FOUND
        else:
            profile.maximum_calories = data.get('maximum_calories')
            DB.session.add(profile)
            DB.session.commit()
            response = marshal(profile, PROFILE_MODEL)
            code = CODE_OK
    else:
        response = dict(RESPONSES_CATALOG['no_permission_other_user'])
        response['error'] = response['error'].format(id_user=user_input.id,
                                                     id_user_2=id_user)
        code = CODE_FORBIDDEN
    return response, code


def get_avatar(id_user, user_input):
    """
    Retrieve the a user image profile or avatar
    :param id_user: user id to retrieve the image profile or avatar
    :type: int
    :param user_input: user id to which the image profile belongs
    :type: User Model
    :return: user image profile. HTTP status code
    :type: tuple(image, int)
    """
    roles = get_roles_user(user_input)
    if id_user == user_input.id or roles.intersection({ADMIN_ROLE,
                                                       MANAGER_ROLE}):
        user = User.query.filter(User.id == id_user).first()
        profile = Profile.query.filter(Profile.user_id == id_user).first()
        if not user:
            response = dict(RESPONSES_CATALOG['no_user_server'])
            response['error'] = response['error'].format(id_user=id_user)
            code = CODE_NOT_FOUND
        else:
            path_avatar = os.path.join(APP.config['AVATARS_SAVE_PATH'],
                                       profile.name_picture_l)
            return send_file(path_avatar, mimetype='image/png')
    else:
        response = dict(RESPONSES_CATALOG['no_permission_resource'])
        response['error'] = response['error'].format(id_user=user_input.id)
        code = CODE_FORBIDDEN
    return response, code


def update_avatar(id_user, files, user_input):
    """
    Update of an user image profile. Get file path from files and upload the
    new image to replace the last one stored in the server
    :param id_user: user id corresponding to user to update image profile
    :type: int
    :param files: path to upload the new image from the client
    :type: str
    :param user_input: User who made the request
    :type: User Model
    :return: New Image updated if success, error message otherwise. HTTP status
    code
    :type: tuple(image, int)
    """

    roles = get_roles_user(user_input)
    if id_user == user_input.id or roles.intersection({ADMIN_ROLE,
                                                       MANAGER_ROLE}):
        user = User.query.filter(User.id == id_user).first()
        profile = Profile.query.filter(Profile.user_id == id_user).first()
        if not user:
            response = dict(RESPONSES_CATALOG['no_user_server'])
            response['error'] = response['error'].format(id_user=id_user)
            code = CODE_NOT_FOUND
        else:
            if 'file' not in files:
                return RESPONSES_CATALOG['no_file_found'], CODE_BAD_REQUEST
            file = files['file']
            if file and allowed_file(file.filename):
                try:
                    file.save(os.path.join(APP.config['AVATARS_SAVE_PATH'],
                                           profile.name_picture_l))
                except Exception:
                    response = RESPONSES_CATALOG['internal_error']
                    code = CODE_INTERNAL_ERROR
                    return response, code
            pic = Image.open(os.path.join(APP.config['AVATARS_SAVE_PATH'],
                                          profile.name_picture_l))
            pic_small = pic.resize((SMALL_SIZE_AVATAR, SMALL_SIZE_AVATAR),
                                   Image.ANTIALIAS)
            pic_small.save(os.path.join(APP.config['AVATARS_SAVE_PATH'],
                                        profile.name_picture_s))
            pic_medium = pic.resize((MEDIUM_SIZE_AVATAR, MEDIUM_SIZE_AVATAR),
                                    Image.ANTIALIAS)
            pic_medium.save(os.path.join(APP.config['AVATARS_SAVE_PATH'],
                                         profile.name_picture_m))
            pic_large = pic.resize((LARGE_SIZE_AVATAR, LARGE_SIZE_AVATAR),
                                   Image.ANTIALIAS)
            pic_large.save(os.path.join(APP.config['AVATARS_SAVE_PATH'],
                                        profile.name_picture_l))
            response = RESPONSES_CATALOG['profile_image_changed']
            code = CODE_OK
    else:
        response = dict(RESPONSES_CATALOG['no_permission_other_user'])
        response['error'] = response['error'].format(id_user=user_input.id,
                                                     id_user_2=id_user)
        code = CODE_FORBIDDEN
    return response, code
