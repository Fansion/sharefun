# -*- coding: utf-8 -*-

__author__ = 'frank'

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextField, PasswordField, SelectField, TextAreaField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Length, EqualTo, Email

from models import Work, User


class RegisterForm(Form):

    email = StringField(
        '邮箱*', description='未注册过的邮箱', validators=[DataRequired('邮箱不能为空'), Length(1, 64), Email('邮箱格式不正确')])
    username = TextField(
        '昵称*', description='未被使用过的昵称', validators=[DataRequired('昵称不能为空'), Length(1, 64)])
    password = PasswordField('密码*', validators=[
        DataRequired('密码不能为空'),
        EqualTo('confirm', message='密码不一致，请重新输入密码')]
    )
    confirm = PasswordField(
        '确认*', description='重复输入密码确认', validators=[DataRequired('密码不能为空')])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经被注册过，请更换邮箱')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被使用，请更换用户名')


class SigninForm(Form):

    email = StringField(
        '邮箱*', description='使用已注册过的邮箱', validators=[DataRequired('邮箱不能为空'), Length(1, 64), Email('邮箱格式不正确')])
    password = PasswordField('密码*', validators=[DataRequired('密码不能为空')])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登陆')


class WorkForm(Form):

    cate_id = SelectField(
        '类别', default=1, validators=[DataRequired('作品类别不能为空')], coerce=int)
    title1 = TextField('作品1', description='准确的作品名称')
    title2 = TextField('作品2', description='准确的作品名称')
    title3 = TextField('作品3', description='准确的作品名称')
    title4 = TextField('作品4', description='准确的作品名称')
    title5 = TextField('作品5', description='准确的作品名称')

    recomm_reason1 = TextField('推荐词', description='选填')
    recomm_reason2 = TextField('推荐词', description='选填')
    recomm_reason3 = TextField('推荐词', description='选填')
    recomm_reason4 = TextField('推荐词', description='选填')
    recomm_reason5 = TextField('推荐词', description='选填')

class CommentForm(Form):

    content = TextAreaField(
        '内容', description='知道啥说啥,支持吐槽,此框可拖大,支持markdown', validators=[DataRequired('评论内容不能为空')])
