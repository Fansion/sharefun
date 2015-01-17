# -*- coding: utf-8 -*-

__author__ = 'frank'

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin, AnonymousUserMixin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash

from . import login_manager
from permissions import Permission

import datetime


db = SQLAlchemy()


class Category(db.Model):

    """作品类别"""
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    index = db.Column(db.Integer)

    works = db.relationship(
        'Work', backref='category', lazy='dynamic', order_by='desc(Work.created)')

    recommendations = db.relationship(
        'Recommendation', backref='category', lazy='dynamic', order_by='desc(Recommendation.created)')
    genres = db.relationship('Genre', backref='category', lazy='dynamic')

    @staticmethod
    def insert_cates():
        cates = {'电影': 0}
        for n, i in cates.iteritems():
            category = Category.query.filter_by(name=n).first()
            if category is None:
                category = Category(name=n)
                category.index = i
                db.session.add(category)
        db.session.commit()

    def __repr__(self):
        return '<Category %s>' % self.name

work_genres = db.Table('work_genres',
                       db.Column(
                           'genre_id', db.Integer, db.ForeignKey('genres.id')),
                       db.Column(
                           'work_id', db.Integer, db.ForeignKey('works.id'))
                       )


class Work(db.Model):

    """作品"""
    __tablename__ = 'works'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    director = db.Column(db.String(50))
    author = db.Column(db.String(50))
    genre = db.Column(db.String(50))
    score = db.Column(db.Float)
    desc = db.Column(db.Text)
    url = db.Column(db.String(100))
    cover_url = db.Column(db.String(100))
    cover_path = db.Column(db.String(50))
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    cate_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    comments = db.relationship(
        'Comment', backref='work', lazy='dynamic', order_by='desc(Comment.created)')
    recommendation = db.relationship(
        'Recommendation', backref='work', uselist=False)

    genres = db.relationship(
        'Genre', secondary=work_genres, backref=db.backref('works', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return "Work %s" % self.title


class Genre(db.Model):

    """类型"""
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    cate_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    def __repr__(self):
        return "Genre %s" % self.name


class Comment(db.Model):

    """作品评论"""
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    work_id = db.Column(db.Integer, db.ForeignKey('works.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return "Comment %d" % self.id


class Recommendation(db.Model):

    """推荐"""
    __tablename__ = 'recommendations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    finished = db.Column(db.DateTime)
    remarks = db.Column(db.String(150))
    recomm_reason = db.Column(db.String(150))

    cate_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'), default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    work_id = db.Column(db.Integer, db.ForeignKey('works.id'))

    def __repr__(self):
        return "Recommendation %s" % self.name


class Status(db.Model):

    """状态"""
    __tablename__ = 'statuses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

    recommendations = db.relationship(
        'Recommendation', backref='status', lazy='dynamic', order_by='desc(Recommendation.created)')

    @staticmethod
    def insert_statuses():
        names = ['待审核', '审核通过暂未上架', '审核通过已上架', '审核不通过', '隐藏无效']
        for n in names:
            status = Status.query.filter_by(name=n).first()
            if status is None:
                status = Status(name=n)
                db.session.add(status)
        db.session.commit()

    def __repr__(self):
        return "Status %s" % self.name


class Role(db.Model):

    """角色"""

    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.COMMENT | Permission.RECOMMEND, True),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                role.permissions = roles[r][0]
                role.default = roles[r][1]
                db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return "Role %s" % self.name


class User(UserMixin, db.Model):

    """用户"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    douban_id = db.Column(db.Integer)                            #douban id
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True) #douban_username
    password_hash = db.Column(db.String(128))
    douban_abbr = db.Column(db.String(50))                       #douban uid
    is_activated = db.Column(db.Boolean, default=False)          #默认不激活，不影响非豆瓣用户
    is_banned = db.Column(db.Boolean, default=False)             #是否禁用

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('密码不可读')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    comments = db.relationship(
        'Comment', backref='user', lazy='dynamic', order_by='desc(Comment.created)')
    recommendations = db.relationship(
        'Recommendation', backref='user', lazy='dynamic', order_by='desc(Recommendation.created)')

    @staticmethod
    def insert_admin():
        u = User.query.filter_by(
            email=current_app.config['FLASKY_ADMIN']).first()
        if u is None:
            u = User(email=current_app.config[
                     'FLASKY_ADMIN'], username='root', password=current_app.config['FLASKY_PASSWORD'])
            db.session.add(u)
            db.session.commit()

    @staticmethod
    def insert_anonymous_user():
        u = User.query.filter_by(username='匿名').first()
        if u is None:
            u = User(email=current_app.config[
                     'FLASKY_ANONYMOUS'], username='匿名')
            db.session.add(u)
            db.session.commit()

    def __repr__(self):
        return "User %s" % self.username


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
