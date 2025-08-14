from celery import Celery
from celery.schedules import crontab

app = Celery("merge_xml_files")

app.conf.broker_url = 'redis://localhost:6379/0'

app.autodiscover_tasks([app])


app.conf.beat_schedule = {
    'merge-xml-daily': {
        'task': 'myapp.tasks.merge_xml_files_task',
        'schedule': crontab(hour=10, minute=0),
    },
}