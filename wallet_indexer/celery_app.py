from celery import Celery, signals

from wallet_indexer.settings import wallet_indexer_settings


CELERY_WALLET_FETCH_QUEUE_NAME = "wallet-fetch-queue"
CELERY_NOTICED_WALLETS_UPLOAD_QUEUE_NAME = "noticed-wallets-upload-queue"
CELERY_SYSTEM_QUEUE_NAME = "system-queue"


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
    sender.app.send_task("load-noticed-wallets")


app = create_app()
