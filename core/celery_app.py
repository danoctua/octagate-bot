from celery import Celery

from core.settings import Config


CELERY_WALLET_FETCH_QUEUE_NAME = "wallet-fetch-queue"
CELERY_NOTICED_WALLETS_UPLOAD_QUEUE_NAME = "noticed-wallets-upload-queue"
CELERY_SYSTEM_QUEUE_NAME = "system-queue"


def create_app() -> Celery:
    _app = Celery()
    _app.conf.update(
        {
            "broker_url": Config.broker_url,
            "result_backend": Config.broker_url,
            "include": ["core.tasks"],
        }
    )
    return _app


app = create_app()
