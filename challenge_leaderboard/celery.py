from __future__ import absolute_import, unicode_literals

import django

from celery import Celery
from datetime import datetime, timedelta

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'challenge_leaderboard.settings')
django.setup()

app = Celery('challenge_leaderboard')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'add-every-5-seconds': {
        'task': 'webapp.views.updateList',
        'schedule': 120,
    }
}

app.conf.timezone = 'UTC'

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
