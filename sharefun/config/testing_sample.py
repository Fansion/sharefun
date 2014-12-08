# -*- coding: utf-8 -*-

__author__ = 'frank'

from .default_sample import Config


class TestingConfig(Config):
    TESTING = True

    # disable csrf while testing
    WTF_CSRF_ENABLED = False

    FLASKY_ADMIN = 'admin@testing.com'
    FLASKY_PASSWORD = 'testing'

    # db config
    DB_USER = 'user'
    DB_PASSWORD = 'password'
    DB_HOST = 'host'
    DB_NAME = 'db'
    SQLALCHEMY_DATABASE_URI = "mysql://%s:%s@%s/%s" % (
        DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
