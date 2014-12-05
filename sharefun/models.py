# -*- coding: utf-8 -*-

__author__ = 'frank'

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin, AnonymousUserMixin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash

from . import login_manager
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
        'Recommendation', backref='category', lazy='dynamic', order_by='desc(Work.created)')

    def __repr__(self):
        return '<Category %s>' % self.name


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

    def __repr__(self):
        return "Work %s" % self.title


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

    cate_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'), default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return "Recommendation %s" % self.name


class Status(db.Model):

    """状态"""
    __tablename__ = 'statuses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

    recommendations = db.relationship(
        'Recommendation', backref='status', lazy='dynamic', order_by='desc(Recommendation.created)')

    def __repr__(self):
        return "Status %s" % self.name

from permissions import Permission


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
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

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
