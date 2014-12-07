# -*- coding: utf-8 -*-

__author__ = 'frank'

from .default_sample import Config


class DevelopmentConfig(Config):

    DEBUG = True

    SECRET_KEY = 'development_key'
