"""
Configuration file for Mangiato API
"""

import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'mangiato.db')
SECRET_KEY = "mangia che ti fa bene"
SECURITY_PASSWORD_SALT = 'pasta pizza pepperoni'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
SECURITY_REGISTERABLE = True
AVATARS_SAVE_PATH = os.path.join(BASEDIR, 'avatars/')
WTF_CSRF_ENABLED = True
