# -*- coding: utf-8 -*-
from __future__ import absolute_import

from celery_proj.celery import app
from sharefun import create_app
from sharefun.models import db, Recommendation, User, Category, Comment, Work
from sharefun.script.spider.crawlDoubanWorkInfo import main
from sharefun.config import load_config
from sharefun import get_mail_handler

import os
from subprocess import call
from datetime import datetime, timedelta
from urllib import urlretrieve
import requests

config = load_config()

search_movie_url = "http://api.douban.com/v2/movie/search?q=%s"
movie_url = "http://api.douban.com/v2/movie/subject/%s"


@app.task
def crawller():
    """根据最新推荐抓取相应作品信息
    """
    names_file = open(config.NAMES_PATH, 'a+')
    flask_app = create_app()
    with flask_app.app_context():
        for recommendation in Recommendation.query.filter_by(status_id=2):
            names_file.write(
                recommendation.category.name + ':' + recommendation.name + '\n')
    names_file.close()

    main(config.NAMES_PATH, config.SUCCESSFUL_NAMES_PATH,
         config.FAILED_NAMES_PATH, config.WEBPAGES_PATH, config.COVERS_FOLDER_PATH)

    with flask_app.app_context():
        """打补丁
        目前只发现部分电影信息直接通过crawlDoubanWorkInfo.py无法抓取，需登陆才能在搜索框中搜索到
        通过豆瓣电影api的方式查询到相关电影信息
        """
        for recommendation in Recommendation.query.filter_by(status_id=2):
            movies_info = requests.get(
                search_movie_url % recommendation.name).json()
            if movies_info:
                subjects = movies_info['subjects']
                for subject in subjects:
                    if subject['title'] == recommendation.name:
                        # 先查到指定电影名称的电影id
                        movie_id = subject['id']
                        if movie_id:
                            # 利用电影id直接通过api查询相关电影信息
                            movie_info = requests.get(
                                movie_url % movie_id).json()
                            cover_path = os.path.join(
                                os.path.abspath(os.path.dirname(__name__)), 'sharefun/static/covers', 'movie_' + movie_id + '.jpg')
                            # 下载封面图片
                            if not os.path.exists(cover_path):
                                urlretrieve(
                                    movie_info['images']['large'], cover_path)
                            work = Work(title=recommendation.name, director=movie_info['directors'][0]['name'], genre='/'.join(movie_info['genres']), score=movie_info['rating'][
                                'average'], desc=movie_info['summary'], url=movie_info['alt'], cover_url=movie_info['images']['large'], cover_path=cover_path[cover_path.find('static/') + 7:], created=datetime.utcnow(), cate_id=recommendation.cate_id)
                            db.session.add(work)
                            recommendation.status_id = 3
                            db.session.add(recommendation)
                            db.session.commit()
                        break


@app.task
def send_mail():
    flask_app = create_app()
    info = '新注册用户:\n'
    with flask_app.app_context():
        today = str(datetime.utcnow()).split(' ')[0] + ' 00:00:00.000000'
        for user in User.query.filter(User.created > today):
            info += user.email + '\n'
    if info != '新注册用户:\n':
        import logging
        logger = logging.getLogger('sf')
        logger.addHandler(get_mail_handler())
        logger.error(info)


@app.task
def backup():
    """备份mysql数据库"""
    t = datetime.now().strftime('%y-%m-%d_%H.%M.%S')
    f = 'backup-sf-%s.sql' % t
    call("mysqldump -u%s -p%s --skip-opt --add-drop-table --default-character-set=utf8 --quick sf > %s" %
         (config.DB_USER, config.DB_PASSWORD, os.path.join('/home/frank/sf-backup', f)), shell=True)

# 不包括reading，只有read和wish
collections_url = "https://api.douban.com/v2/book/user/%s/collections"
collection_url = "https://api.douban.com/v2/book/%s/collection"


@app.task
def sync_with_douban(access_token=None):
    """在豆瓣用户初始激活账户一小时之类抓取其评论数据
    定时任务时access_token为空，push相关的操作都没有access_token
    当授权登陆时会产生合法的access_token，调用同步任务执行相关的push操作
    """
    headers = {
        "Authorization": "Bearer %s" % access_token}
    flask_app = create_app()
    with flask_app.app_context():
        one_hour_ago = datetime.utcnow() + timedelta(hours=-1)
        print one_hour_ago
        for user in User.query.filter_by(is_activated=1):
            print user.douban_abbr
            #　不需要豆瓣读书相关的权限
            collections_info = requests.get(
                collections_url % user.douban_abbr).json()
            if collections_info:
                recommendations = Recommendation.query.filter_by(status_id=3).filter_by(
                    user_id=user.id).filter(Recommendation.finished > one_hour_ago).all()
                work_dict = {}
                for recommendation in recommendations:
                    work_dict[recommendation.work.url.strip(
                        '/').split('/')[-1]] = recommendation.work
                print work_dict

                collection_ids = []
                collections = collections_info["collections"]
                if collections:
                    comments = Comment.query.filter_by(user_id=user.id).filter(
                        Comment.created > one_hour_ago).all()
                    # crawl comments
                    # 在豆瓣上已读并已评论的作品中选出其中在系统中已上架的作品，将豆瓣上的评论抓取到本地
                    for collection in collections:
                        collection_ids.append(collection['book']['id'])
                        # 已上架作品
                        work = Work.query.filter_by(
                            url=collection['book']['alt']).first()
                        if work:
                            # 已读并豆瓣上评论过
                            if collection['status'] == 'read' and collection['comment']:
                                # comment = Comment.query.filter_by(
                                #     content=collection['comment']).first()
                                comment = Comment.query.filter_by(
                                    user_id=user.id).filter_by(work_id=work.id).first()
                                # 该评论没有被抓取，则新增评论添加到系统
                                if not comment:
                                    # 豆瓣上评论时间为utc+8，变为utc+0存到服务器
                                    comment = Comment(
                                        content=collection['comment'], user_id=user.id,  work_id=work.id, created=datetime.strptime(collection['updated'], "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8))
                                else:  # 若系统中已经添加了该评论，则直接修改内容
                                    comment.content = collection['comment']
                                print comment.content
                                db.session.add(comment)
                                db.session.commit()

                    print comments
                    print config.DOUBAN_CLIENT_ID
                    print access_token
                    print headers

                    if access_token:
                        for collection in collections:
                            # push comments
                            # 将系统中已上架作品的评论同步到豆瓣
                            # 需要权限，目前会失败
                            for comment in comments:
                                if comment.user_id == user.id and collection['book']['alt'] == comment.work.url:
                                    data = {
                                        'status': collection['status'],
                                        'comment': comment.content,
                                        'scope': 'douban_basic_common'
                                    }
                                    res = requests.put(
                                        collection_url % collection['book']['id'], data, headers=headers)
                                    print res.status_code
                                    print res.content
                                    print comment
                                    break

                        # push recommendations
                        # 在系统中推荐，将推荐作品同步到豆瓣收藏
                        # 需要权限，目前会失败
                        print collection_ids
                        for work_id, work in work_dict.iteritems():
                            if not work_id in collection_ids:
                                data = {
                                    'status': 'read',
                                    'comment': work.recommendation.recomm_reason,
                                    'scope': 'douban_basic_common'
                                }
                                res = requests.post(
                                    collection_url % work_id, data,  headers=headers)
                                print res.status_code
                                print res.content


@app.task
def add(x, y):
    return x + y
