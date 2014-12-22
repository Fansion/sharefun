# -*- coding: utf-8 -*-

__author__ = 'frank'

import markdown2
from flask.ext.login import current_user


def markdown(text):
    return markdown2.markdown(text)


def normalize(output):
    """将null或者empty转换为暂无输出"""
    if not output:
        return '暂无'
    else:
        return output


def engrolename_chinrolename(engrolename):
    s = {'Administrator': '管理员', 'User': '普通用户'}
    return s[engrolename]


def ismyself(username):
    if current_user.is_authenticated() and current_user.username == username:
        return "我"
    else:
        return username
