# -*- coding: utf-8 -*-

__author__ = 'frank'
"""执行celery操作是在外部的sharefun/下，
爬虫本身用的是相对路径，如果外部直接执行爬虫就涉及到相对路径的问题。
所以不能直接使用spider_config.py中的配置
"""
