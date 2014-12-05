# -*- coding: utf-8 -*-

__author__ = 'frank'

import markdown2


def markdown(text):
    return markdown2.markdown(text)


def cateid_to_catename(cateid):
    d = {1: '电影'}
    return d[cateid]


def statusid_to_statusname(status_id):
    d = {1: '待审核', 2: '审核通过已上架', 3: '审核通过暂未上架', 4: '审核不通过', 5: '隐藏无效'}
    return d[status_id]


def normalize(output):
    """将null或者empty转换为暂无输出"""
    if not output:
        return '暂无'
    else:
        return output
