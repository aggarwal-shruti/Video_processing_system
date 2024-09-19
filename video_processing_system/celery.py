from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_processing_system.settings')


app = Celery('video_processing_system')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(['VP_app'])

# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')
