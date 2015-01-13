# -*- coding: utf-8 -*-

__author__ = 'frank'

from flask import render_template, Blueprint, redirect, url_for,  flash
from flask.ext.login import login_required, current_user

from ..forms import WorkForm, CommentForm
from ..models import db, Category,  Comment, Recommendation, User

bp = Blueprint('user', __name__)


@bp.route('/secret')
@login_required
def secret():
    return 'Secret'


@bp.route('/recommend', methods=['GET', 'POST'])
def recommend():
    form = WorkForm()
    form.cate_id.choices = [(t.id, t.name)
                            for t in Category.query.order_by(Category.index)]
    if form.validate_on_submit():
        names = [form.title1.data.strip(), form.title2.data.strip(
        ), form.title3.data.strip(), form.title4.data.strip(), form.title5.data.strip()]
        recomm_reasons = [form.recomm_reason1.data.strip(), form.recomm_reason2.data.strip(
        ), form.recomm_reason3.data.strip(), form.recomm_reason4.data.strip(), form.recomm_reason5.data.strip()]
        cate_id = form.cate_id.data
        hasName = False
        hasRepetition = False
        repeatedNames = ' '
        for name in names:
            if name:
                # 判断是否存在
                if not Recommendation.query.filter(Recommendation.cate_id == cate_id).filter(Recommendation.name == name).first():
                    if current_user.is_authenticated():
                        recommendation = Recommendation(
                            name=name, cate_id=cate_id, remarks='', user_id=current_user.id, recomm_reason=recomm_reasons[names.index(name)])
                    else:
                        anonymous_user = User.query.filter_by(username='匿名').first()
                        if anonymous_user:
                            recommendation = Recommendation(
                                name=name, cate_id=cate_id, remarks='', user_id=anonymous_user.id, recomm_reason=recomm_reasons[names.index(name)])
                        else:
                            u = User(username='匿名')
                            db.session.add(u)
                            db.session.commit()
                            recommendation = Recommendation(
                                name=name, cate_id=cate_id, remarks='', user_id=u.id, recomm_reason=recomm_reasons[names.index(name)])
                    db.session.add(recommendation)
                else:
                    if name not in repeatedNames:
                        repeatedNames += '<<' + name + '>>'
                    hasRepetition = True
                hasName = True
        if hasRepetition:
            # 清空表单
            form.title1.data = form.title2.data = form.title3.data = form.title4.data = form.title5.data = ''
            form.recomm_reason1.data = form.recomm_reason2.data = form.recomm_reason3.data = form.recomm_reason4.data = form.recomm_reason5.data = ''

            flash(repeatedNames + '曾被推荐过,再提交些新鲜货吧亲')
            return render_template('user/recommend.html', form=form)
        if not hasName:
            flash(repeatedNames + '至少推荐一些再提交吧亲')
            return render_template('user/recommend.html', form=form)
        db.session.commit()
        return redirect(url_for('site.recommendations'))
    if not current_user.is_authenticated():
        flash('建议先注册，之后再推荐作品！')
    return render_template('user/recommend.html', form=form)
