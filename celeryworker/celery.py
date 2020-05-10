from celery import Celery
from configuration.app_config import CeleryConfig

celery_app = Celery('celeryworker', broker=CeleryConfig.BROKER, include=['celeryworker.tasks'])

if __name__ == '__main__':
    celery_app.start()
