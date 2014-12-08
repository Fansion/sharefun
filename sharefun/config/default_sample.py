# -*- coding: utf-8 -*-

__author__ = 'frank'
import os


class Config:
    # set True in development
    DEBUG = False
    TESTING = False

    # administrator
    FLASKY_ADMIN = 'admin@default.com'
    FLASKY_PASSWORD = 'default'

    # number
    FLASK_COMMENTS_PER_PAGE = 5

    # app config
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 7
    SESSION_COOKIE_NAME = 'default_session'

    # db config
    DB_USER = 'user'
    DB_PASSWORD = 'password'
    DB_HOST = 'host'
    DB_NAME = 'db'
    SQLALCHEMY_DATABASE_URI = "mysql://user:password@host/db"

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # used as a general-purpose encryption key by Flask and several
    # third-party extensions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    # toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # smtp config
    SMTP_SERVER = ""
    SMTP_PORT = 25
    SMTP_USER = ""
    SMTP_PASSWORD = ""
    SMTP_FROM = ""
    SMTP_ADMIN = ""

    # Redis
    REDIS = False  # 是否启用Redis
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 1

    # for crawller
    # 从外部sharefun目录下调用script时，需要用到对应的绝对路径
    CURRENT_DIR = os.path.abspath(os.path.pardir)
    # 写死的路径
    # -------------------------------------
    SPIDER_BASE_DIR = 'sharefun/script/spider'
    COVERS_BASE_PATH = 'sharefun/static/covers'
    # -------------------------------------
    NAMES_PATH = os.path.join(CURRENT_DIR, SPIDER_BASE_DIR, 'names')
    SUCCESSFUL_NAMES_PATH = os.path.join(
        CURRENT_DIR, SPIDER_BASE_DIR, 'successful_names')
    FAILED_NAMES_PATH = os.path.join(
        CURRENT_DIR, SPIDER_BASE_DIR, 'failed_names')
    WEBPAGES_PATH = os.path.join(CURRENT_DIR, SPIDER_BASE_DIR, 'webpages')
    COVERS_FOLDER_PATH = os.path.join(CURRENT_DIR, COVERS_BASE_PATH)
