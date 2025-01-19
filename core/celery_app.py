from celery import Celery

from core.settings import Config


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
