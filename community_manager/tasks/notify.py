import asyncio

from celery.utils.log import get_task_logger
from telethon import Button
from telethon.extensions import markdown

from community_manager.celery_app import app
from core.constants import (
    CELERY_SYSTEM_QUEUE_NAME,
    MIGRATION_TO_ACCESS_TEXT,
    MIRATION_TO_ACCESS_BUTTON_URL,
    MIGRATION_TO_ACCESS_BUTTON_TEXT,
)
from core.services.db import DBService
from core.services.supertelethon import TelethonService
from core.services.user import UserService

logger = get_task_logger(__name__)


async def async_notify_migration_single(telegram_user_id: int) -> None:
    telethon_service = TelethonService()
    await telethon_service.start()

    try:
        await telethon_service.send_message(
            chat_id=telegram_user_id,
            text=MIGRATION_TO_ACCESS_TEXT.replace("\\", ""),
            buttons=[
                Button.url(
                    text=MIGRATION_TO_ACCESS_BUTTON_TEXT,
                    url=MIRATION_TO_ACCESS_BUTTON_URL,
                )
            ],
            parse_mode=markdown.parse,
            link_preview=False,
        )
        logger.info("Message sent to user %d", telegram_user_id)
    except Exception:
        logger.exception("Unable to send message to user %d", telegram_user_id)
    finally:
        await telethon_service.stop()


@app.task(
    name="notify-migration-single",
    queue=CELERY_SYSTEM_QUEUE_NAME,
)
def notify_migration_single(telegram_user_id: int) -> None:
    asyncio.run(async_notify_migration_single(telegram_user_id=telegram_user_id))


@app.task(
    name="notify-migration-all",
    queue=CELERY_SYSTEM_QUEUE_NAME,
)
def notify_migration_all() -> None:
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        users = user_service.get_all()[:10]
        for user in users:
            notify_migration_single.apply_async(args=(user.telegram_id,))
