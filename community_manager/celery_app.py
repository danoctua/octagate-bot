from celery import Celery
from celery.schedules import crontab

from community_manager.settings import community_manager_settings


def create_app() -> Celery:
    _app = Celery()
    _app.conf.update(
        {
            "broker_url": community_manager_settings.broker_url,
            "result_backend": community_manager_settings.broker_url,
            "include": ["community_manager.tasks"],
            "worker_concurrency": community_manager_settings.worker_concurrency,
            "beat_schedule": {
                "check-chat-members": {
                    "task": "check-chat-members",
                    "schedule": crontab(minute="*/1"),  # Every minute
                },
                "refresh-chat-external-sources": {
                    "task": "refresh-chat-external-sources",
                    "schedule": crontab(minute="*/3"),  # Every 3 minutes
                },
            },
            "beat_schedule_filename": community_manager_settings.beat_schedule_filename,
        }
    )
    return _app


app = create_app()
