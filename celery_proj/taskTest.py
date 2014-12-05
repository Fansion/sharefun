# -*- coding: utf-8 -*-
from __future__ import absolute_import

from sharefun.script.spider.crawlDoubanWorkInfo import main
from sharefun.config import load_config

def crawllerTest():

    main(config.NAMES_PATH, config.SUCCESSFUL_NAMES_PATH,
         config.FAILED_NAMES_PATH, config.WEBPAGES_PATH, config.COVERS_FOLDER_PATH)
"""需在当前目录父目录，sharefun下执行"""
crawllerTest()
