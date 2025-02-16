import asyncio
import logging

from community_manager.celery_app import app
from community_manager.settings import community_manager_settings
from core.actions.authorization import AuthorizationAction
from core.constants import (
    CELERY_SYSTEM_QUEUE_NAME,
    UPDATED_WALLETS_SET_NAME,
    DISCONNECTED_WALLETS_SET_NAME,
)
from core.services.chat import TelegramChatUserService
from core.services.db import DBService
from core.services.superredis import RedisService
from core.services.wallet import WalletService

logger = logging.getLogger(__name__)


async def sanity_chat_checks(
    wallets: list[str] | None, disconnected_users_ids: list[int] | None
) -> None:
    logger.info(f"Validating chat members for {wallets}")
    with DBService().db_session() as db_session:
        wallet_service = WalletService(db_session)
        if wallets:
            all_wallets = wallet_service.get_all(addresses=wallets)
            user_ids = {wallet.user_id for wallet in all_wallets}
        else:
            user_ids = set()

        if disconnected_users_ids:
            user_ids |= set(disconnected_users_ids)

        if not user_ids:
            logger.info("No users to validate. Skipping")
            return

        telegram_chat_user_service = TelegramChatUserService(db_session)
        chat_members = telegram_chat_user_service.get_all(user_ids=list(user_ids))
        authorization_action = AuthorizationAction(db_session)
        await authorization_action.kick_ineligible_chat_members(
            chat_members=chat_members
        )


@app.task(
    name="check-chat-members",
    queue=CELERY_SYSTEM_QUEUE_NAME,
)
def check_chat_members() -> None:
    if not community_manager_settings.enable_manager:
        logger.info("Community manager is disabled.")
        return

    redis_service = RedisService()
    wallets = redis_service.pop_from_set(
        name=UPDATED_WALLETS_SET_NAME,
        count=community_manager_settings.items_per_task,
    )
    # Query all of them as most of the disconnected users will not be part of any chat
    disconnected_users_ids = redis_service.pop_from_set(
        name=DISCONNECTED_WALLETS_SET_NAME
    )

    if isinstance(wallets, str):
        wallets = [wallets]

    if isinstance(disconnected_users_ids, str):
        disconnected_users_ids = [disconnected_users_ids]
    elif not disconnected_users_ids:
        disconnected_users_ids = []

    disconnected_users_ids = [int(user_id) for user_id in disconnected_users_ids]

    if wallets or disconnected_users_ids:
        try:
            asyncio.run(
                sanity_chat_checks(
                    wallets=wallets, disconnected_users_ids=disconnected_users_ids
                )
            )
        except Exception as exc:
            # Add wallets back to the set to retry later
            logger.error(f"Failed to validate chat members: {exc}", exc_info=True)
            redis_service.add_to_set(
                DISCONNECTED_WALLETS_SET_NAME,
                *[str(user_id) for user_id in disconnected_users_ids],
            )
            redis_service.add_to_set(UPDATED_WALLETS_SET_NAME, *wallets)
    else:
        logger.info("No users to validate. Skipping")

    if community_manager_settings.enable_manager:
        app.send_task(
            name="check-chat-members",
            queue=CELERY_SYSTEM_QUEUE_NAME,
            countdown=60,
        )
