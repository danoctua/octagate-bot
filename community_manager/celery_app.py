from celery import Celery, signals

from community_manager.settings import community_manager_settings
from core.constants import CELERY_SYSTEM_QUEUE_NAME


def create_app() -> Celery:
    _app = Celery()
    _app.conf.update(
        {
            "broker_url": community_manager_settings.broker_url,
            "result_backend": community_manager_settings.broker_url,
            "include": ["community_manager.tasks"],
            "worker_concurrency": community_manager_settings.worker_concurrency,
        }
    )
    return _app


@signals.worker_ready.connect
def at_start(sender, **kwargs):
    if community_manager_settings.enable_manager:
        sender.app.send_task("check-chat-members", queue=CELERY_SYSTEM_QUEUE_NAME)


app = create_app()
