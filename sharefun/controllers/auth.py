# -*- coding: utf-8 -*-

__author__ = 'frank'

from flask import Blueprint, render_template, redirect, url_for, request,  session, flash
from flask.ext.login import login_user, logout_user, login_required

from ..forms import SigninForm, RegisterForm
from ..models import db, Status, Recommendation, User
from ..decorators import logout_required

import datetime

bp = Blueprint('auth', __name__)


@bp.route('/register/', methods=['GET', 'POST'])
@logout_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登陆')
        return redirect(url_for('auth.signin'))
    return render_template('auth/register.html', form=form)


@bp.route('/signin', methods=['GET', 'POST'])
@logout_required
def signin():
    form = SigninForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('该邮箱尚未注册，请重新登陆')
            return render_template('auth/signin.html', form=form)
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('site.index'))
        flash('邮箱或密码错误，请重新登陆')
    return render_template('auth/signin.html', form=form)


@bp.route('/signout/')
@login_required
def signout():
    logout_user()
    flash('成功登出,欢迎再次登入')
    return redirect(url_for('site.index'))
