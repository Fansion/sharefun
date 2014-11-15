# -*- coding: utf-8 -*-

__author__ = 'frank'

from flask import Flask, request, url_for, render_template
from flask_wtf.csrf import CsrfProtect
from flask_debugtoolbar import DebugToolbarExtension

from . import config

def register_jinja(app):

    # inject vars into template context
    @app.context_processor
    def inject_vars():
        return dict()

    # url generator for pagination
    def url_for_other_page(page):
        view_args = request.view_args.copy()
        args = request.args.copy().to_dict()
        args['page'] = page
        view_args.update(args)
        return url_for(request.endpoint, **view_args)

    app.jinja_env.globals['url_for_other_page'] = url_for_other_page

def register_routes(app):
    from .controllers import admin, site, movie
    app.register_blueprint(site.bp, url_prefix='')
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(movie.bp, url_prefix='/movie')

def register_error_handle(app):
    @app.errorhandler(403)
    def page_403(error):
        return render_template('site/403.html'), 403

    @app.errorhandler(404)
    def page_404(error):
        return render_template('site/404.html'), 404

    @app.errorhandler(500)
    def page_500(error):
        return render_template('site/500.html'), 500

def register_db(app):
    from .models import db
    db.init_app(app)

def register_logger(app):
    """send error log to admin by smtp"""
    if not app.debug:
        import logging
        from logging.handlers import  SMTPHandler
        credentials = (config.SMTP_USER, config.SMTP_PASSWORD)
        mail_handler = SMTPHandler((config.SMTP_SERVER, config.SMTP_PORT), config.SMTP_FROM,
                                   config.SMTP_ADMIN,'sc-log', credentials)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # CSRF protect
    CsrfProtect(app)

    if app.debug:
        DebugToolbarExtension(app)

    register_jinja(app)
    register_routes(app)
    register_error_handle(app)
    register_db(app)
    register_logger(app)

    @app.before_request
    def before_request():
        pass

    return app

app = create_app()