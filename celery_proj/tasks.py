# -*- coding: utf-8 -*-
from __future__ import absolute_import

from celery_proj.celery import app

from sharefun import create_app
from sharefun.models import db, Recommendation
from sharefun.script.spider.crawlDoubanWorkInfo import main
from sharefun.config import NAMES_PATH, SUCCESSFUL_NAMES_PATH, FAILED_NAMES_PATH, WEBPAGES_PATH, COVERS_FOLDER_PATH
from sharefun.filters import cateid_to_catename

import os


@app.task
def crawller():
    """根据最新推荐抓取相应作品信息"""
    names_file = open(NAMES_PATH, 'a+')
    flask_app = create_app()
    with flask_app.app_context():
        for recommendation in Recommendation.query.filter_by(status_id=2):
            names_file.write(
                cateid_to_catename(recommendation.cate_id) + ':' + recommendation.name + '\n')
    names_file.close()

    main(NAMES_PATH, SUCCESSFUL_NAMES_PATH,
         FAILED_NAMES_PATH, WEBPAGES_PATH, COVERS_FOLDER_PATH)


@app.task
def add(x, y):
    return x + y
