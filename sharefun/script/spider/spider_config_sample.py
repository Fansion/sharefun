# -*- coding: utf-8 -*-

__author__ = 'frank'

SEARCH_URL_PATTERN = 'http://{cate_name}.douban.com/subject_search?search_text={work_title}'
# cates name->folder name
CATENAME_CHIN_TO_ENG = {'电影': 'movie', '图书': 'book'}
CATENAME_TO_CATEID = {'电影': 1}


# db
dbHOST = 'host'
dbNAME = 'db'
dbWORKSNAME = 'works'
dbRECOMMSNAME = 'recommendations'
dbUSER = 'user'
dbPASSWORD = 'password'

# for crawller
# 在当前spider目录下执行爬虫，外部调用main执行爬虫路径会出错
import os
CURRENT_DIR = os.path.abspath(os.path.dirname(__name__))
NAMES_PATH = os.path.join(CURRENT_DIR, 'names')
SUCCESSFUL_NAMES_PATH = os.path.join(CURRENT_DIR, 'successful_names')
FAILED_NAMES_PATH = os.path.join(CURRENT_DIR, 'failed_names')
WEBPAGES_PATH = os.path.join(CURRENT_DIR, 'webpages')
COVERS_FOLDER_PATH =  os.path.join(CURRENT_DIR.replace('/script/spider',''), 'static/covers')
