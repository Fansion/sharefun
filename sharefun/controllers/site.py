# -*- coding: utf-8 -*-

__author__ = 'frank'

from flask import render_template, Blueprint, redirect, url_for, request, flash
from flask.ext.login import current_user

from ..forms import WorkForm, CommentForm
from ..models import db, Category, Work, Comment, Recommendation, Status
from ..config import FLASK_COMMENTS_PER_PAGE

import os
from datetime import datetime

bp = Blueprint('site', __name__)


@bp.route('/')
def index():
    """首页"""
    works = Work.query.order_by(Work.cate_id, Work.created.desc())
    newest_comments = Comment.query.order_by(Comment.created.desc()).limit(5)
    return render_template('site/index.html', works=works, newest_comments=newest_comments, current_time=datetime.utcnow())


@bp.route('/about')
def about():
    """关于"""
    return render_template('site/about.html')


@bp.route('/work/<int:work_id>', methods=['GET', 'POST'])
def work(work_id):
    """详情页"""
    form = CommentForm()
    work = Work.query.get_or_404(work_id)
    if form.validate_on_submit() and current_user.is_authenticated():
        content = form.content.data.strip()
        comment = Comment(
            content=content, user_id=current_user.id,  work_id=work.id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('site.work', work_id=work.id))
    return render_template('site/work.html', work=work, form=form)


@bp.route('/comments', defaults={'page': 1})
@bp.route('/comments/page/<int:page>')
def comments(page):
    """所有评论页"""
    comments = Comment.query.order_by(Comment.created.desc()).paginate(page, FLASK_COMMENTS_PER_PAGE, error_out=True)
    return render_template('site/comments.html', comments=comments)


@bp.route('/recommendations')
def recommendations():
    statusids_recommendations = [
        (s.id, s.recommendations) for s in Status.query.order_by(Status.id)]
    return render_template('site/recommendations.html', statusids_recommendations=statusids_recommendations)
