# -*- coding: utf-8 -*-
from __future__ import absolute_import

from celery_proj.celery import app

from sharefun import create_app
from sharefun.models import db, Recommendation
from sharefun.script.spider.crawlDoubanWorkInfo import main
from sharefun.config import load_config
from sharefun.filters import cateid_to_catename

import os

config = load_config()


@app.task
def crawller():
    """根据最新推荐抓取相应作品信息"""
    names_file = open(config.NAMES_PATH, 'a+')
    flask_app = create_app()
    with flask_app.app_context():
        for recommendation in Recommendation.query.filter_by(status_id=2):
            names_file.write(
                cateid_to_catename(recommendation.cate_id) + ':' + recommendation.name + '\n')
    names_file.close()

    main(NAMES_PATH, config.SUCCESSFUL_NAMES_PATH,
         config.FAILED_NAMES_PATH, config.WEBPAGES_PATH, config.COVERS_FOLDER_PATH)


@app.task
def add(x, y):
    return x + y
