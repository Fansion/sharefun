# -*- coding: utf-8 -*-

__author__ = 'frank'

from flask import Blueprint, render_template, redirect, url_for, request,  session, flash
from flask.ext.login import login_user, logout_user, login_required

from ..forms import SigninForm, RegisterForm, SingleRecommendationForm
from ..models import db, Status, Recommendation, User, Category, work_genres, Work
from ..decorators import admin_required, permission_required

import datetime

bp = Blueprint('admin', __name__)

# 判断是否具有某一特定权限
# @permission_required(Permission.MODERATE_COMMENTS)


@bp.route('/recommendations/audit/')
@login_required
@admin_required
def audit():
    statusids_recommendations = [
        (s.id, s.recommendations) for s in Status.query.order_by(Status.id)]
    return render_template('site/recommendations.html', statusids_recommendations=statusids_recommendations)


@bp.route('/recommendation/edit/<int:recomm_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_recommendation(recomm_id):
    recommendation = Recommendation.query.get_or_404(recomm_id)
    form = SingleRecommendationForm(obj=recommendation)
    form.cate_id.choices = [(t.id, t.name)
                            for t in Category.query.order_by(Category.index)]
    form.status_id.choices = [(t.id, t.name)
                              for t in Status.query.order_by(Status.id)]
    form.user_id.choices = [(t.id, t.username)
                            for t in User.query.order_by(User.id)]
    if form.validate_on_submit():
        recommendation.name = form.name.data
        recommendation.remarks = form.remarks.data
        recommendation.recomm_reason = form.recomm_reason.data
        recommendation.cate_id = form.cate_id.data
        recommendation.status_id = form.status_id.data
        recommendation.user_id = form.user_id.data
        recommendation.finished = datetime.datetime.utcnow()
        db.session.add(recommendation)
        db.session.commit()
        return redirect(url_for('admin.audit'))
    return render_template('site/recommendation.html', form=form, recommendation=recommendation)


@bp.route('/recommendations/audit/<int:recomm_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def audit_recommenations(recomm_id):
    recommendation = Recommendation.query.get_or_404(recomm_id)
    """审核与真正处理数据中间相隔一定时间，所以将审核通过状态分为通过未上架（默认）和通过已上架，增加删除待审核推荐"""
    if 'hide' in request.form:
        recommendation.status_id = 5      # 设置为隐藏无效状态
    if 'yes' in request.form:
        recommendation.status_id = 2
    if 'no' in request.form:
        recommendation.status_id = 4
    if 'yes-append' in request.form:
        recommendation.remarks = recommendation.remarks + \
            request.form.get('remarks')
    elif 'yes-modify' in request.form:
        recommendation.remarks = request.form.get('remarks')
    recommendation.finished = datetime.datetime.utcnow()
    db.session.add(recommendation)
    db.session.commit()
    return redirect(url_for('admin.audit'))
