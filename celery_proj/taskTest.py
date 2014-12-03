# -*- coding: utf-8 -*-
from __future__ import absolute_import

from sharefun.script.spider.crawlDoubanWorkInfo import main
from sharefun.config import NAMES_PATH, SUCCESSFUL_NAMES_PATH, FAILED_NAMES_PATH, WEBPAGES_PATH, COVERS_FOLDER_PATH


def crawllerTest():

    main(NAMES_PATH, SUCCESSFUL_NAMES_PATH,
         FAILED_NAMES_PATH, WEBPAGES_PATH, COVERS_FOLDER_PATH)
"""需在当前目录父目录，sharefun下执行"""
crawllerTest()
