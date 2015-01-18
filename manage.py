# -*- coding: utf-8 -*-

__author__ = 'frank'


from flask.ext.script import Manager, Shell
from sharefun import app
from sharefun.models import db, User, Role, Permission, Category, Status, Genre, Work
from flask.ext.migrate import Migrate, MigrateCommand


manager = Manager(app)

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


def make_context():
    return dict(app=app, db=db, User=User, Role=Role, Category=Category, Status=Status, Permission=Permission, Genre=Genre, Work=Work)
manager.add_command("shell", Shell(make_context=make_context))


@manager.command
def test():
    """测试"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def run():
    app.run(debug=True)


@manager.command
def crawller():
    """手动执行抓取操作"""
    from celery_proj.tasks import crawller

    crawller.delay()


@manager.command
def sync_with_douban():
    """手动执行抓取评论"""
    from celery_proj.tasks import sync_with_douban

    sync_with_douban.delay()


@manager.command
def backup():
    """手动备份数据库"""
    from celery_proj.tasks import backup

    backup.delay()


@manager.command
def send_mail():
    """手动发送邮件通知"""
    from celery_proj.tasks import add, send_mail

    # add.delay(int(x), int(y))
    send_mail.delay()

if __name__ == '__main__':
    manager.run()
