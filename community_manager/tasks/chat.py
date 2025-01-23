import asyncio
import logging

from community_manager.celery_app import app
from community_manager.settings import community_manager_settings
from core.actions.authorization import AuthorizationAction
from core.constants import CELERY_SYSTEM_QUEUE_NAME, UPDATED_WALLETS_SET_NAME
from core.services.chat import TelegramChatUserService
from core.services.db import DBService
from core.services.superredis import RedisService
from core.services.wallet import WalletService

logger = logging.getLogger(__name__)


async def sanity_chat_checks(wallets: list[str]) -> None:
    logger.info(f"Validating chat members for {wallets}")
    with DBService().db_session() as db_session:
        wallet_service = WalletService(db_session)
        all_wallets = wallet_service.get_all(addresses=wallets)

        user_ids = [wallet.user_id for wallet in all_wallets]

        telegram_chat_user_service = TelegramChatUserService(db_session)
        chat_members = telegram_chat_user_service.get_all(user_ids=user_ids)
        authorization_action = AuthorizationAction(db_session)
        await authorization_action.kick_ineligible_chat_members(
            chat_members=chat_members
        )


@app.task(
    name="check-chat-members",
    queue=CELERY_SYSTEM_QUEUE_NAME,
)
def check_chat_members() -> None:
    redis_service = RedisService()
    wallets = redis_service.pop_from_set(name=UPDATED_WALLETS_SET_NAME, count=100)

    if not wallets and community_manager_settings.enable_manager:
        logger.info("No wallets to check.")
        app.send_task(
            name="check-chat-members",
            queue=CELERY_SYSTEM_QUEUE_NAME,
            countdown=60,
        )
        return
    elif isinstance(wallets, str):
        wallets = [wallets]

    asyncio.run(sanity_chat_checks(wallets=wallets))

    if community_manager_settings.enable_manager:
        app.send_task(
            name="check-chat-members",
            queue=CELERY_SYSTEM_QUEUE_NAME,
            countdown=60,
        )
