# -*- coding: utf-8 -*-

__author__ = 'frank'

from flask import render_template, Blueprint, redirect, url_for, request, flash, current_app
from flask.ext.login import current_user

from ..forms import WorkForm, CommentForm
from ..models import db, Category, Work, Comment, Recommendation, Status, User, Genre, work_genres

import os
from datetime import datetime

bp = Blueprint('site', __name__)


@bp.route('/')
def index():
    """首页"""
    genre_id = request.args.get('genre_id', 0, int)
    page = request.args.get('page', 1, int)
    cate_id = request.args.get('cate_id', 1, int)
    works = Work.query.filter_by(cate_id=cate_id).order_by(Work.created.desc())
    # 按照类型对应的作品数对类型排序
    from sqlalchemy import func
    genres = [genre for genre, count in db.session.query(Genre, func.count(work_genres.c.work_id).label(
        'total')).filter_by(cate_id=cate_id).join(work_genres).group_by(Genre).order_by('total desc').all()]
    if genre_id:
        # use join
        # works = works.join(Genre.works).filter(Genre.id == genre_id)
        if genre_id == -1:
            works = Work.query.order_by(func.rand())
        else:
            works = works.filter(Work.genres.any(id=genre_id))

    newest_comments = Comment.query.order_by(Comment.created.desc()).limit(5)
    total = Recommendation.query.count()
    success = Recommendation.query.filter(
        Recommendation.status_id == 3).count()
    failure = Recommendation.query.filter(
        Recommendation.status_id == 4).count()
    works = works.paginate(
        page, current_app.config['FLASK_WORKS_PER_PAGE'], error_out=True)
    return render_template('site/index.html', works=works, newest_comments=newest_comments, current_time=datetime.utcnow(), total=total, success=success, failure=failure, genres=genres, genre_id=genre_id, page=page, cate_id=cate_id)


@bp.route('/about')
def about():
    """关于"""
    return render_template('site/about.html')


@bp.route('/work/<int:work_id>', methods=['GET', 'POST'])
def work(work_id):
    """详情页"""
    form = CommentForm()
    q = Work.query
    work = q.get_or_404(work_id)
    prev = q.filter(Work.id > work_id).order_by(Work.id).first()
    next = q.filter(Work.id < work_id).order_by(Work.id.desc()).first()
    print prev,':',next
    genres = []
    for genre in work.genres:
        genres.append(genre)
    if form.validate_on_submit() and current_user.is_authenticated():
        content = form.content.data.strip()
        comment = Comment(
            content=content, user_id=current_user.id,  work_id=work.id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('site.work', work_id=work.id))
    return render_template('site/work.html', work=work, form=form, genres=genres, prev=prev, next=next)


@bp.route('/user/<int:id>')
def user(id):
    user = User.query.get_or_404(id)
    success_recomms_count = Recommendation.query.filter(
        Recommendation.user_id == id, Recommendation.status_id == 3).count()
    comments_count = Comment.query.filter(Comment.user_id == id).count()
    return render_template('site/user.html', user=user, success_recomms_count=success_recomms_count, comments_count=comments_count)


@bp.route('/comments')
def comments():
    """所有评论页"""
    user_id = request.args.get('user_id', 0, int)
    page = request.args.get('page', 1, int)
    comments = Comment.query.order_by(Comment.created.desc())
    # 只显示有评论的user
    users = [user for user in User.query.all() if user.comments.count()]
    # 按照评论数量倒序对user排序
    users = sorted(
        users, lambda u1, u2: cmp(u1.comments.count(), u2.comments.count()), reverse=True)
    if user_id:
        comments = comments.filter(Comment.user_id == user_id)
    comments = comments.paginate(
        page, current_app.config['FLASK_COMMENTS_PER_PAGE'], error_out=True)
    return render_template('site/comments.html', comments=comments, users=users, user_id=user_id)


@bp.route('/recommendations')
def recommendations():
    statusids_recommendations = [
        (s.id, s.recommendations) for s in Status.query.order_by(Status.id)]
    return render_template('site/recommendations.html', statusids_recommendations=statusids_recommendations)
