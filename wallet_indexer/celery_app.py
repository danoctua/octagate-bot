from celery import Celery, signals

from core.constants import CELERY_NOTICED_WALLETS_UPLOAD_QUEUE_NAME
from wallet_indexer.settings import wallet_indexer_settings


def create_app() -> Celery:
    _app = Celery()
    _app.conf.update(
        {
            "broker_url": wallet_indexer_settings.broker_url,
            "result_backend": wallet_indexer_settings.broker_url,
            "include": ["wallet_indexer.tasks"],
            "worker_concurrency": wallet_indexer_settings.worker_concurrency,
        }
    )
    return _app


@signals.worker_ready.connect
def at_start(sender, **kwargs):
    sender.app.send_task(
        "load-noticed-wallets", queue=CELERY_NOTICED_WALLETS_UPLOAD_QUEUE_NAME
    )


app = create_app()
