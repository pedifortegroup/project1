import os

from pathlib import Path

# basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '7676mnbcdnb'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(Path().absolute(), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
