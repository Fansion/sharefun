# -*- coding: utf-8 -*-

__author__ = 'frank'

import hashlib
from flask import render_template, url_for, current_app, session
from flask_mail import Message, Mail

mail = Mail()


def signup_mail(user):
    """Send signup email"""
    config = current_app.config
    token = hashlib.sha1(user.username).hexdigest()
    url = config.get(
        'SITE_DOMAIN') + url_for('auth.douban_activate', douban_id=user.douban_id, token=token)
    msg = Message("欢迎来到sharefun", recipients=[user.email])
    msg.html = render_template('auth/email.html', url=url)
    mail.send(msg)


def signin_user(user, permenent):
    """Sign in user"""
    # session.permanent = permenent
    session['signin_method'] = 'by_douban'      # 如果豆瓣登陆则不要求验证邮箱
    session['user_id'] = user.id                # 此处是user_id而不是douban_id


def signout_user():
    """Sign in user"""
    session.pop('user_id', None)
