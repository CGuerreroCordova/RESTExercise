import os
import sys
from setuptools import (setup, find_packages, )

NAME = "mangiato"
SCRIPT = [os.path.join('mangiato','__main__.py')]
DESCRIPTION = "Provide an API to register jogging_api.py from users"
here = os.path.abspath(os.path.dirname(__file__))
INSTALL_REQUIREMENTS = ["flask==2.3.2", "flask_restplus==0.12.1",
                        "passlib==1.7.1", "pyparsing==2.3.1","pyopenssl",
                        "flask-avatars==0.2.1", "flask-wtf==0.14.2", 
                        "flask-httpauth==3.2.4", "sqlalchemy==1.2.17",
                        "flask_sqlalchemy==2.3.2"]


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name=NAME,
    version="0.1",
    license='CGGC',
    author="CGGC",
    keywords="",
    setup_requires=["pytest-runner"] if 'test' in sys.argv else [],
    tests_require=["pytest==3.9.3","pytest-cov","coverage"],
    install_requires=INSTALL_REQUIREMENTS,
    author_email="cguerrerocordova@gmail.com",
    description=DESCRIPTION,
    long_description='Server to register meals and calories per day',
    packages=find_packages(exclude=['tests*']),
    package_data={'': ['cert.pem', 'key.pem']},
    include_package_data=True,
    platforms='any',
    classifiers=[],
    scripts=SCRIPT,
)
