# -*- coding: utf-8 -*-

__author__ = 'frank'

from flask import Blueprint, render_template, redirect, url_for, request,  session, flash
from flask.ext.login import login_user, logout_user, login_required

from ..forms import SigninForm, RegisterForm
from ..models import db, Status, Recommendation, User
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


@bp.route('/recommendations/audit/<int:recomm_id>', methods=['POST'])
@login_required
@admin_required
def audit_recommenation(recomm_id):
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
    else:
        recommendation.remarks = request.form.get('remarks')
    recommendation.finished = datetime.datetime.utcnow()
    db.session.add(recommendation)
    db.session.commit()
    return redirect(url_for('admin.audit'))
