from celery import Celery
import os

def make_celery():
    broker = os.getenv('CELERY_BROKER', 'pyamqp://guest:guest@localhost//')
    backend = os.getenv('CELERY_BACKEND', 'db+sqlite:///celery.sqlite')
    celery = Celery('proj', broker=broker, backend=backend)
    return celery

celery = make_celery()
