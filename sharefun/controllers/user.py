# -*- coding: utf-8 -*-

__author__ = 'frank'

from flask import render_template, Blueprint, redirect, url_for,  flash
from flask.ext.login import login_required, current_user

from ..forms import WorkForm, CommentForm
from ..models import db, Category,  Comment, Recommendation

bp = Blueprint('user', __name__)


@bp.route('/secret')
@login_required
def secret():
    return 'Secret'


@bp.route('/recommend', methods=['GET', 'POST'])
@login_required
def recommend():
    form = WorkForm()
    form.cate_id.choices = [(t.id, t.name)
                            for t in Category.query.order_by(Category.index)]
    if form.validate_on_submit():
        names = [form.title1.data.strip(), form.title2.data.strip(
        ), form.title3.data.strip(), form.title4.data.strip(), form.title5.data.strip()]
        cate_id = form.cate_id.data
        hasName = False
        hasRepetition = False
        repeatedNames = ' '
        for name in names:
            if name:
                # 判断是否存在
                if not Recommendation.query.filter(Recommendation.cate_id == cate_id).filter(Recommendation.name == name).first():
                    recommendation = Recommendation(
                        name=name, cate_id=cate_id, remarks='', user_id=current_user.id)
                    db.session.add(recommendation)
                else:
                    if name not in repeatedNames:
                        repeatedNames += '<<' + name + '>>'
                    hasRepetition = True
                hasName = True
        if hasRepetition:
            # 清空表单
            form.title1.data = form.title2.data = form.title3.data = form.title4.data = form.title5.data = ''
            flash(repeatedNames + '曾被推荐过,再提交些新鲜货吧亲')
            return render_template('user/recommend.html', form=form)
        if not hasName:
            flash(repeatedNames + '至少推荐一些再提交吧亲')
            return render_template('user/recommend.html', form=form)
        db.session.commit()
        return redirect(url_for('site.recommendations'))
    return render_template('user/recommend.html', form=form)
