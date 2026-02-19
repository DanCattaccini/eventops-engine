import os
from celery import Celery

BROKER_URL = os.environ["CELERY_BROKER_URL"]

celery_app = Celery("eventops", broker=BROKER_URL)

@celery_app.task(name="eventops.ping")
def ping():
    return "pong"