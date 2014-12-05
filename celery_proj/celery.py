# -*- coding: utf-8 -*-
from __future__ import absolute_import

from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

app = Celery('celery_proj',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0',
             include=['celery_proj.tasks'])

app.conf.update(
    CELERY_TIMEZONE='Asia/Shanghai',
    CELERYBEAT_SCHEDULE={
        'crawller': {
            'task': 'celery_proj.tasks.crawller',
            # 'schedule': timedelta(seconds=10)
            'schedule': crontab(hour='0,6,12,18', minute=0)
        }
    }
)


if __name__ == '__main__':
    app.start()
