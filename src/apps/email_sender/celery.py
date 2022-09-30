from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from .email import send_mail_from_to, send_activation_mail


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

app.config_from_object('django.conf:settings', namespace='CELERY')
#app.conf.update(BROKER_URL=os.environ['REDIS_URL'],CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.task(name="send_activation_mail_async_task")
def send_activation_mail_async_task(**kwargs):
    return send_activation_mail(**kwargs)

@app.task(name="send_mail_async_task")
def send_mail_async_task(camp_id):

    return send_mail_from_to(camp_id)
    