"""
Provide an instance of database and method to reset_database
"""
import datetime
from flask_sqlalchemy import SQLAlchemy
from mangiato.constants import ADMIN_ROLE, MANAGER_ROLE

DB = SQLAlchemy()


def reset_database():
    """
    Drop all tables in database and create again empty, create by default
    admin and manager users
    :return:
    """
    from mangiato.database.models import User, Role, Profile, Invitation
    DB.drop_all()
    DB.create_all()
    # DB.session.add(Role('admin', "CRUD all records and users."))
    # DB.session.add(Role('manager', "CRUD only users."))
    # DB.session.add(Role('common_user', "CRUD on their owned records."))
    # admin_user = User(email='admin@admin.com',
    #                   password='admin',
    #                   first_name='Master',
    #                   last_name='OfScience',
    #                   confirmed=True,
    #                   confirmed_on=datetime.datetime.now()
    #                   )
    # role_admin = Role.query.filter(Role.name == ADMIN_ROLE).first()
    # admin_user.roles.append(role_admin)
    # profile = Profile(admin_user)
    # DB.session.add(profile)
    # DB.session.add(admin_user)
    # DB.session.commit()
    #
    # manager_user = User(email='manager@manager.com',
    #                     password='manager',
    #                     first_name='Golden',
    #                     last_name='Master',
    #                     confirmed=True,
    #                     confirmed_on=datetime.datetime.now()
    #                     )
    # role_manager = Role.query.filter(Role.name == MANAGER_ROLE).first()
    # manager_user.roles.append(role_manager)
    # profile = Profile(manager_user)
    # DB.session.add(profile)
    # DB.session.add(manager_user)
    # DB.session.commit()
