# -*- coding: utf-8 -*-

__author__ = 'frank'

from .default import Config


class DevelopmentConfig(Config):

    DEBUG = True

    SECRET_KEY = 'development_key'
