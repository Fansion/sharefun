# -*- coding: utf-8 -*-

__author__ = 'frank'

from flask import render_template, Blueprint

bp = Blueprint('site', __name__)

@bp.route('/')
def index():
    """首页"""
    return render_template('site/index.html')

@bp.route('/about')
def about():
    """关于"""
    return render_template('site/about.html')