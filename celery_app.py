from celery import Celery
from celery.schedules import crontab
import os


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


def make_celery():
    celery = Celery(
        "proj",
        broker=REDIS_URL,
        backend=REDIS_URL,
    )

    celery.conf.update(
        timezone="America/Sao_Paulo",
        imports=["tasks.tasks"],
        beat_schedule={
            "verificar-reservas-diariamente": {
                "task": "tasks.tasks.verificar_reservas",
                "schedule": crontab(hour=9, minute=0),
            },
        },
    )

    return celery


celery = make_celery()
