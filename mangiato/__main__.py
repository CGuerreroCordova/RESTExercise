"""
Module of execution of Mangiato API
"""

from mangiato.mangiato_api import APP, initialize_app, run_app, add_users

if __name__ == '__main__': # pragma: no cover
    initialize_app(APP, "app_config.py")
    run_app()
