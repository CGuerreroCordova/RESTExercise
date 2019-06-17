from datetime import datetime

NEW_USER = {
    "first_name": "Cristian",
    "last_name": "Guerrero",
    "username": "newuser@postpost.com",
    "password": "demonios"
}

ADMIN_USERNAME = 'admin@admin.com'
ADMIN_PASSWORD = 'admin'

MANAGER_USERNAME = 'manager@manager.com'
MANAGER_PASSWORD = 'manager'

USERS_LIST_ADMIN = {
    "items": [
        {
            "meals": [],
            "id": 1,
            "username": "admin@admin.com",
            "first_name": "Master",
            "last_name": "OfScience",
            "confirmed": True,
            "confirmed_on": datetime.now().strftime('%Y-%m-%d'),
            "attempts_login": 0,
            "blocked": False,
            "roles": [
                {
                    "name": "admin",
                    "description": "CRUD all records and users."
                }
            ]
        },
        {
            "meals": [],
            "id": 2,
            "username": "manager@manager.com",
            "first_name": "Golden",
            "last_name": "Master",
            "confirmed": True,
            "confirmed_on": datetime.now().strftime('%Y-%m-%d'),
            "attempts_login": 0,
            "blocked": False,
            "roles": [
                {
                    "name": "manager",
                    "description": "CRUD only users."
                }
            ]
        },
        {
            "meals": [],
            "id": 3,
            "username": "newuser@postpost.com",
            "first_name": "Cristian",
            "last_name": "Guerrero",
            "confirmed": True,
            "confirmed_on": datetime.now().strftime('%Y-%m-%d'),
            "attempts_login": 0,
            "blocked": False,
            "roles": [
                {
                    "name": "common_user",
                    "description": "CRUD on their owned records."
                }
            ]
        }
    ],
    "page": 1,
    "pages": 1,
    "per_page": 10,
    "total": 3
}

USERS_LIST_MANAGER = {
    "items": [
        {
            "id": 1,
            "username": "admin@admin.com",
            "first_name": "Master",
            "last_name": "OfScience",
            "confirmed": True,
            "confirmed_on": datetime.now().strftime('%Y-%m-%d'),
            "attempts_login": 0,
            "blocked": False,
            "roles": [
                {
                    "name": "admin",
                    "description": "CRUD all records and users."
                }
            ]
        },
        {
            "id": 2,
            "username": "manager@manager.com",
            "first_name": "Golden",
            "last_name": "Master",
            "confirmed": True,
            "confirmed_on": datetime.now().strftime('%Y-%m-%d'),
            "attempts_login": 0,
            "blocked": False,
            "roles": [
                {
                    "name": "manager",
                    "description": "CRUD only users."
                }
            ]
        },
        {
            "id": 3,
            "username": "newuser@postpost.com",
            "first_name": "Cristian",
            "last_name": "Guerrero",
            "confirmed": True,
            "confirmed_on": datetime.now().strftime('%Y-%m-%d'),
            "attempts_login": 0,
            "blocked": False,
            "roles": [
                {
                    "name": "common_user",
                    "description": "CRUD on their owned records."
                }
            ]
        }
    ],
    "page": 1,
    "pages": 1,
    "per_page": 10,
    "total": 3
}

USER_ADMIN = {
    "meals": [],
    "id": 3,
    "username": "newuser@postpost.com",
    "first_name": "Cristian",
    "last_name": "Guerrero",
    "confirmed": True,
    "confirmed_on": datetime.now().strftime('%Y-%m-%d'),
    "attempts_login": 0,
    "blocked": False,
    "roles": [
        {
            "name": "common_user",
            "description": "CRUD on their owned records."
        }
    ]
}

USER_MANAGER = {
    "id": 3,
    "username": "newuser@postpost.com",
    "first_name": "Cristian",
    "last_name": "Guerrero",
    "confirmed": True,
    "confirmed_on": datetime.now().strftime('%Y-%m-%d'),
    "attempts_login": 0,
    "blocked": False,
    "roles": [
        {
            "name": "common_user",
            "description": "CRUD on their owned records."
        }
    ]
}

new_meal = {
	"date": "2019-02-25",
	"time": "12:00:00",
	"description": "meat"
}

meal_update = {
	"date": "2019-02-15",
	"time": "13:00:00",
	"description": "fish"
}

meal_patch = {
    "date": "2019-01-15",
	"time": "13:00:00",
}

meal_patch_2 = {
	"description": "fish"
}

response_new_meal = {
    "meal_id": 1,
    "date": "2019-02-25",
    "time": "12:00:00",
    "description": "meat",
    "calories": 226,
    "calories_less_expected": True
}

response_meal_updated_1 = {
    "meal_id": 1,
    "date": "2019-02-15",
    "time": "13:00:00",
    "description": "fish",
    "calories": 226,
    "calories_less_expected": True
}

profile = {
    "maximum_calories": 2250
}

profile_update = {
    "maximum_calories": 5000
}

NEW_INVITATION = {
	"email":"newuser_2@postpost.com",
}

NEW_INVITATION_2 = {
	"email":"newuser@postpost.com",
}

INVITATION_CREATE = {
    "id": 1,
    "email": "newuser_2@postpost.com",
    "status": "pending"
}

ACCEPTANCE_PART = b"""<h3 style="text-align: center;">Please fill in the following fields to complete your registration</h3>"""

ACCEPTANCE_PART_2 = b"""<h1 style="text-align: center;"><span style="color: #ff6600;">Accepting invitation to Mangiato:</span></h1>"""

ACCEPTATION_DATA = {'first_name': "Medicham",
                    'last_name': "hectorez",
                    'password':'secreto'}

UPDATE_USER = {
            "id" : 3,
            "username": "newuser@postpost.com",
            "first_name": "Isenberg",
            "last_name": "Morris",
            "confirmed": True,
            "confirmed_on": datetime.now().strftime('%Y-%m-%d'),
            "attempts_login": 1,
            "blocked": False,
            "roles": [
                {
                    "name": "common_user",
                    "description": "CRUD on their owned records."
                }
            ]
        }

PATCH_USER = {
            "first_name": "Isenberg",
            "confirmed": True,
            "attempts_login": 2,
            "blocked": False,
        }

PATCH_USER_2 = {
            "username": "newuser@postpost.com",
            "last_name": "fluorescent",
            "confirmed_on": datetime.now().strftime('%Y-%m-%d'),
            "roles": [
                {
                    "name": "manager",
                    "description": "CRUD only users."
                }
            ]
}

PATCHED_USER = {
            "id" : 3,
            "username": "newuser@postpost.com",
            "first_name": "Isenberg",
            "last_name": "Guerrero",
            "confirmed": True,
            "confirmed_on": datetime.now().strftime('%Y-%m-%d'),
            "attempts_login": 2,
            "blocked": False,
            "roles": [
                {
                    "name": "common_user",
                    "description": "CRUD on their owned records."
                }
            ]
        }

PATCHED_USER_2 = {
            "id" : 3,
            "username": "newuser@postpost.com",
            "first_name": "Isenberg",
            "last_name": "fluorescent",
            "confirmed": True,
            "confirmed_on": datetime.now().strftime('%Y-%m-%d'),
            "attempts_login": 2,
            "blocked": False,
            "roles": [
                {
                    "name": "manager",
                    "description": "CRUD only users."
                }
            ]
        }


UPDATE_USER_FIRST_NAME_MISSING = {
            "id" : 3,
            "username": "newuser@postpost.com",
            "last_name": "Morris",
            "confirmed": True,
            "confirmed_on": datetime.now().strftime('%Y-%m-%d'),
            "attempts_login": 1,
            "blocked": False,
            "roles": [
                {
                    "name": "common_user",
                    "description": "CRUD on their owned records."
                }
            ]
        }

FIRST_NAME_MISSING_FAIL = {'errors':
                             {'first_name':
                                  "'first_name' is a required property"},
                         'message': 'Input payload validation failed'}

PATCH_INVITATION = {'status': 'accepted'}
PATCH_INVITATION_EMAIL = {'email': 'nuevoinvitado@correo.com'}

MEAL_1 = {
	"date": "2019-02-01",
	"time": "09:00:00",
	"description": "eggs",
    "calories": 1500
}
MEAL_2 = {
	"date": "2019-02-01",
	"time": "12:00:00",
	"description": "meat",
    "calories": 800
}
MEAL_3 = {
	"date": "2019-02-01",
	"time": "16:00:00",
	"description": "bread",
    "calories": 700
}
MEAL_4 = {
	"date": "2019-02-02",
	"time": "09:00:00",
	"description": "sugar",
    "calories": 150
}
MEAL_5 = {
	"date": "2019-02-02",
	"time": "15:50:00",
	"description": "rice",
    "calories": 678
}
MEAL_6 = {
	"date": "2019-02-02",
	"time": "21:00:00",
	"description": "pork",
    "calories": 678
}
MEAL_7 = {
	"date": "2019-02-03",
	"time": "08:50:00",
	"description": "cheese",
    "calories": 123
}
MEAL_8 = {
	"date": "2019-02-03",
	"time": "21:00:00",
	"description": "elephant",
    "calories": 15777
}

MEAL_9 = {
	"date": "2019-02-03",
	"time": "21:10:00",
	"description": "elephant",
    "calories": 3000
}

ERROR_QUERY_FIELDS = "type object 'Meal' has no attribute 'calries'"
UNBLOCK_USER = { "blocked": False }
DUMMY_USER = {
    "first_name": "dummy",
    "last_name": "dummy",
    "username": "dummyuser@dummy.com",
    "password": "dummypass"
}

MEALS = ['meat', 'rice', 'eggs', 'cheese', 'sugar', 'apple', 'bread',
         'ice cream', 'banana', 'pork', 'fruit', 'pizza', 'taco']
