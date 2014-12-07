# -*- coding: utf-8 -*-

__author__ = 'frank'

from .default import Config


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
