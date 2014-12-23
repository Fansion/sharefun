# -*- coding: utf-8 -*-
from __future__ import absolute_import

from celery_proj.celery import app

from sharefun import create_app
from sharefun.models import db, Recommendation, User, Category
from sharefun.script.spider.crawlDoubanWorkInfo import main
from sharefun.config import load_config
from sharefun import get_mail_handler

import os
from subprocess import call
from datetime import datetime

config = load_config()


@app.task
def crawller():
    """根据最新推荐抓取相应作品信息"""
    names_file = open(config.NAMES_PATH, 'a+')
    flask_app = create_app()
    with flask_app.app_context():
        for recommendation in Recommendation.query.filter_by(status_id=2):
            names_file.write(recommendation.category.name + ':' + recommendation.name + '\n')
    names_file.close()

    main(config.NAMES_PATH, config.SUCCESSFUL_NAMES_PATH,
         config.FAILED_NAMES_PATH, config.WEBPAGES_PATH, config.COVERS_FOLDER_PATH)


@app.task
def send_mail():
    flask_app = create_app()
    info = '新注册用户:\n'
    with flask_app.app_context():
        today = str(datetime.now()).split(' ')[0] + ' 00:00:00.000000'
        for user in User.query.filter(User.created > today):
            info += user.email + '\n'
    if info != '新注册用户:\n':
        import logging
        logger = logging.getLogger('sf')
        logger.addHandler(get_mail_handler())
        logger.error(info)


@app.task
def backup():
    """备份mysql数据库"""
    t = datetime.now().strftime('%y-%m-%d_%H.%M.%S')
    f = 'backup-sf-%s.sql' % t
    call("mysqldump -u%s -p%s --skip-opt --add-drop-table --default-character-set=utf8 --quick sf > %s" %
         (config.DB_USER, config.DB_PASSWORD, os.path.join('/home/frank/sf-backup', f)), shell=True)


@app.task
def add(x, y):
    return x + y
