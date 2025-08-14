import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()


BROKER_URL = os.getenv("BROKER_URL", "redis://localhost:6379/0")
TIMEZONE = os.getenv("TIMEZONE", "Europe/Kyiv")

app = Celery("prom_feed", Broker=BROKER_URL, timezone=TIMEZONE)

app.conf.timezone = TIMEZONE
app.conf.enable_utc = True


app.conf.beat_schedule = {
    'merge-xml-daily': {
        'task': 'parsing_and_merged_xml_files.tasks.merge_xml_files_task',
        'schedule': crontab(hour=10, minute=0),
    },
}