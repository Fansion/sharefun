# -*- coding: utf-8 -*-

__author__ = 'frank'


from flask.ext.script import Manager
from sharefun import app, models

manager = Manager(app)

@manager.command
def run():
    # the server will automatically reload for code changes
    # and show a debugger in case an exception happened
    app.run(debug=True)

@manager.command
def syncdb():
    models.db.create_all()

if __name__ == '__main__':
    manager.run()