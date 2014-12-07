# -*- coding: utf-8 -*-

__author__ = 'frank'


from flask.ext.script import Manager, Shell
from sharefun import app
from sharefun.models import db, User, Role, Permission, Category, Status
from flask.ext.migrate import Migrate, MigrateCommand


manager = Manager(app)

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


# """进入server初始化数据库"""
# Category.insert_cates()
# Role.insert_roles()
# Status.insert_statuses()
# User.insert_admin()
def make_context():
    return dict(app=app, db=db, User=User, Role=Role, Category=Category, Status=Status, Permission=Permission)
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


if __name__ == '__main__':
    manager.run()
