# -*- coding: utf-8 -*-

__author__ = 'frank'

from .default import Config


class ProductionConfig(Config):

    FLASKY_ADMIN = 'admin@production.com'

    # db config
    DB_USER = 'www-data'
    DB_PASSWORD = 'www-data'
    DB_HOST = 'localhost'
    DB_NAME = 'sf'

    SECRET_KEY = '6.Z;;Op02;EgK4&l`E~>%9~*ol325M'
