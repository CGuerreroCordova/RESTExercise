"""
Declare and provide models database
"""

from hashlib import md5
from flask import request, g, url_for
from sqlalchemy import Enum
from passlib.context import CryptContext
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from mangiato.database import DB
from mangiato.constants import (LIMITS_ATTEMPTS_LOGIN,
                                AVERAGE_CALORIES_PER_DAY, PENDING, ACCEPTED)
from mangiato.globals import AUTH, generate_avatar
from mangiato.app_config import SECRET_KEY


ROLES_USERS = DB.Table('roles_users',
                       DB.Column('user_id', DB.Integer(),
                                 DB.ForeignKey('users.id')),
                       DB.Column('role_id', DB.Integer(),
                                 DB.ForeignKey('roles.id')))
CRYPT = CryptContext(schemes=["sha256_crypt", "md5_crypt", "des_crypt"])


class User(DB.Model):
    """Store users server information"""

    __tablename__ = "users"

    id = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String, unique=True, nullable=False)
    password = DB.Column(DB.String, nullable=False)
    first_name = DB.Column(DB.String, nullable=False)
    last_name = DB.Column(DB.String, nullable=False)
    confirmed = DB.Column(DB.Boolean, nullable=False, default=False)
    confirmed_on = DB.Column(DB.DateTime, nullable=True)
    attempts_login = DB.Column(DB.Integer, nullable=False, default=0)
    blocked = DB.Column(DB.Boolean, nullable=False, default=False)
    roles = DB.relationship('Role', secondary=ROLES_USERS,
                            backref=DB.backref('users', lazy='dynamic'))

    def __init__(self, email, first_name, last_name, password, confirmed=False,
                 confirmed_on=None):
        self.username = email
        self.password = self._hash_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on

    @staticmethod
    def _hash_password(password):
        return CRYPT.hash(password)

    def verify_password(self, password):
        return CRYPT.verify(password, self.password)

    def generate_auth_token(self, expiration=600):
        serial = Serializer(SECRET_KEY, expires_in=expiration)
        return serial.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        serial = Serializer(SECRET_KEY)
        try:
            data = serial.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = User.query.get(data['id'])
        return user

    def __repr__(self):
        return '<models.User[username=%s]>' % self.username


class Role(DB.Model):
    """
    Store Roles information in the server
    """
    __tablename__ = 'roles'

    id = DB.Column(DB.Integer(), primary_key=True)
    name = DB.Column(Enum('admin', 'manager', 'common_user'), unique=True)
    description = DB.Column(DB.String(255))

    def __init__(self, name, description=""):
        self.name = name
        self.description = description

    def __repr__(self):
        return '<models.Role[name=%s]>' % self.name


class Meal(DB.Model):
    """
    Store meals information in the server
    """

    __tablename__ = "meals"
    meal_id = DB.Column(DB.Integer, primary_key=True)
    date = DB.Column(DB.Date, nullable=False)
    time = DB.Column(DB.Time, nullable=False)
    description = DB.Column(DB.String, nullable=False)
    calories = DB.Column(DB.Integer)
    calories_less_expected = DB.Column(DB.Boolean, nullable=False,
                                       default=False)
    user_id = DB.Column(DB.Integer,
                        DB.ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False)
    user = DB.relationship('User',
                           backref=DB.backref('meals', lazy='dynamic',
                                              cascade="all,delete"))

    def __init__(self, date, time, description_meal, calories, user):
        self.date = date
        self.time = time
        self.description = description_meal
        self.calories = calories
        self.user = user
        self.calories_less_expected = None

    def __repr__(self):
        return '<models.Meal[meal_id=%d]>' % self.meal_id


class Profile(DB.Model):
    """
    Store profiles information in the server. Maximum calories and path to
    profile image
    """
    __tablename_ = 'profiles'
    id = DB.Column(DB.Integer, primary_key=True)
    maximum_calories = DB.Column(DB.Integer, default=0)
    name_picture_s = DB.Column(DB.String(100))
    name_picture_m = DB.Column(DB.String(100))
    name_picture_l = DB.Column(DB.String(100))
    user_id = DB.Column(DB.Integer, DB.ForeignKey('users.id',
                                                  ondelete="CASCADE"))
    user = DB.relationship('User', backref=DB.backref('profiles',
                                                      lazy='dynamic',
                                                      cascade="all,delete"))

    def __init__(self, user, name_picture=None,
                 maximum_calories=AVERAGE_CALORIES_PER_DAY):
        self.maximum_calories = maximum_calories
        self.user = user
        if not name_picture:
            code_file_name = md5(user.username.encode('utf-8')).hexdigest()
            self.name_picture_s = generate_avatar(code_file_name)[0]
            self.name_picture_m = generate_avatar(code_file_name)[1]
            self.name_picture_l = generate_avatar(code_file_name)[2]
        else:
            self.name_picture = name_picture


class Invitation(DB.Model):
    """
    Store invitation performed in the server, pending and accepted
    """
    __tablename__ = 'invitations'

    id = DB.Column(DB.Integer(), primary_key=True)
    email = DB.Column(DB.String, unique=True, nullable=False)
    status = DB.Column(DB.Enum(PENDING, ACCEPTED), default=PENDING)

    def __init__(self, email):
        self.email = email

    def accept(self):
        """
        Set invitation status to accepted
        :return: None
        :type: void
        """
        self.status = ACCEPTED


@AUTH.verify_password
def verify_password(username_or_token, password):
    """
    Perform username, and password or token authentication
    :param username_or_token: username or token
    :type: str
    :param password: password
    :type: str
    :return: Decide if password or token was verified. Error otherwise. HTTP
    status code
    :type: boolean
    """
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user:
            g.error = 'Invalid token or username non registered.'
            return False
        if user.blocked:
            g.error = 'This user has been blocked because it has reached ' \
                      'the maximum number of failed login attempts: ' + \
                      str(LIMITS_ATTEMPTS_LOGIN)
            return False
        elif not user.confirmed:
            error_not_confirmation = 'This account has not been confirmed ' \
                                     'yet. Please check your email to ' \
                                     'activate.'
            attempts = user.attempts_login
            attempts = attempts + 1
            if attempts >= LIMITS_ATTEMPTS_LOGIN:
                user.blocked = True
                g.error = 'This user has been blocked because it has ' \
                          'reached the maximum number of failed login ' \
                          'attempts: ' + str(LIMITS_ATTEMPTS_LOGIN)
            else:
                g.error = error_not_confirmation + ' Remaining attempts: ' + \
                          str(LIMITS_ATTEMPTS_LOGIN - attempts)
            user.attempts_login = attempts
            DB.session.add(user)
            DB.session.commit()
            return False
        elif not user.verify_password(password):
            url_login = url_for('api.v1/login_login')
            if request.path == url_login[:-1]:
                attempts = user.attempts_login
                attempts = attempts + 1
                if attempts >= LIMITS_ATTEMPTS_LOGIN:
                    user.blocked = True
                    g.error = 'This user has been blocked because it has ' \
                              'reached the maximum number of failed login ' \
                              'attempts: ' + \
                              str(LIMITS_ATTEMPTS_LOGIN)
                else:
                    g.error = 'Invalid password. Remaining attempts: ' + \
                              str(LIMITS_ATTEMPTS_LOGIN - attempts)
                user.attempts_login = attempts
                DB.session.add(user)
                DB.session.commit()
            else:
                g.error = "Don't have permission to access to this resource"
            return False
    g.user = user
    return True
