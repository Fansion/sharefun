# -*- coding: utf-8 -*-

__author__ = 'frank'

from flask import Blueprint, render_template, redirect, url_for, request,  session, flash, current_app
from flask.ext.login import login_user, logout_user, login_required

from ..forms import SigninForm, RegisterForm, SignupForm
from ..models import db, Status, Recommendation, User
from ..decorators import logout_required
from ..utils import signup_mail,  signin_user, signout_user

import datetime
import requests
import hashlib

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

# 说明：
# 登入系统有两种途径，一直接在本站注册登陆无需验证邮箱，直接登陆；二用豆瓣登陆，需验证邮箱
# 其中直接在本站注册登陆同样会将user_id存入session（login_user函数），豆瓣登陆将douban_id存入session的user_id(signin_user函数)中
#
# session中存储内容类似：
# csrf_token 05b2c11c12465135d664eb27ff79ceee45c275a7
# _fresh True
# user_id 39
# _id 7e987c7c53125f1d833c61e97033dd20
#
# 每次请求之前会检查当前登陆方式，如果是豆瓣登陆则会检查该账户是否被激活及是否被禁止，直接注册登陆不检查状态
# 直接注册登陆退出使用flask_login的logout_user，豆瓣登陆退出时使用signout_user


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
            flash('欢迎登陆ShareFun')
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('site.index'))
        flash('邮箱或密码错误，请重新登陆')
    return render_template('auth/signin.html', form=form)


@bp.route('/douban_pre_signin')
@logout_required
def douban_pre_signin():
    config = current_app.config
    return redirect(config.get('DOUBAN_LOGIN_URL'))


@bp.route('/douban_signin')
@logout_required
def douban_signin():
    """通过豆瓣OAuth登陆
    user_id实际是User表中的douban_id字段
    """
    # get current authed user id
    code = request.args.get('code')
    if not code:
        return redirect(url_for('site.index'))
    url = "https://www.douban.com/service/auth2/token"
    config = current_app.config
    data = {
        'client_id': config.get('DOUBAN_CLIENT_ID'),
        'client_secret': config.get('DOUBAN_SECRET'),
        'redirect_uri': config.get('DOUBAN_REDIRECT_URI'),
        'grant_type': 'authorization_code',
        'code': code
    }
    res = requests.post(url, data=data).json()
    if 'douban_user_id' not in res:
        return redirect(url_for('site.index'))

    user_id = int(res['douban_user_id'])
    user = User.query.filter_by(douban_id=user_id).first()
    if user:
        if user.is_banned:
            flash('账户已被禁用， 请联系管理员')
            signout_user()
            return redirect(url_for('site.index'))
        if not user.is_activated:
            flash('账户尚未激活，请先登陆' + user.email + '查收验证邮件激活账户')
            signout_user()
            return redirect(url_for('site.index'))

        flash('欢迎使用豆瓣账户登陆ShareFun')
        signin_user(user, True)
        redirect_url = url_for('site.index')
        return redirect(redirect_url)
    # 通过加密的session传递user_id数据，防止恶意注册
    session['signup_user_id'] = user_id
    return redirect(url_for('auth.douban_signup'))


@bp.route('/douban_signup', methods=['GET', 'POST'])
@logout_required
def douban_signup():
    """发送激活邮件
    user_id实际是User表中的douban_id字段
    """
    if not 'signup_user_id' in session:
        abort(403)

    user_id = int(session['signup_user_id'])
    user = User.query.filter_by(douban_id=user_id).first()
    if user:
        abort(403)

    # Get user info from douban
    url = "https://api.douban.com/v2/user/%d" % user_id
    user_info = requests.get(url).json()
    form = SignupForm()
    if form.validate_on_submit():
        to_addr = form.email.data
        user = User(
            douban_id=user_id, username=user_info['name'], email=to_addr, douban_abbr=user_info['uid'])
        db.session.add(user)
        db.session.commit()
        # send activate email
        try:
            signup_mail(user)
        except:
            flash('邮件发送失败，请稍后尝试')
        else:
            flash('激活邮件已发送到你的邮箱，请查收激活')
        signout_user()
        session.pop('signup_user_id')
        return redirect(url_for('site.index'))
    return render_template('auth/douban_signup.html', user_info=user_info, form=form)


@bp.route('/activate/<int:douban_id>/<token>')
@logout_required
def douban_activate(douban_id, token):
    # douban_id和token在链接中顺序不影响
    user = User.query.filter_by(douban_id=douban_id).first()
    if token == hashlib.sha1(user.username).hexdigest():
        user.is_activated = True
        db.session.add(user)
        db.session.commit()
        signin_user(user, True)
        flash('账号激活成功，欢迎光临ShareFun')
        return redirect(url_for('site.index'))
    flash('无效的激活链接')
    return redirect(url_for('site.index'))


@bp.route('/signout/')
@login_required
def signout():
    logout_user()
    flash('成功登出,欢迎再次登入')
    return redirect(url_for('site.index'))
