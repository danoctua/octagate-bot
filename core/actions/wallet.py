import logging

from sqlalchemy.orm import Session

from core.actions.base import BaseAction
from core.constants import DEFAULT_WALLET_TRACK_EXPIRATION
from core.services.chat import TelegramChatUserService
from core.services.superredis import RedisService
from core.services.supertelethon import TelethonService
from core.services.wallet import WalletService, UserWalletExistError
from wallet_indexer.celery_app import app
from core.utils.task import wait_for_task

logger = logging.getLogger(__name__)


class WalletAction(BaseAction):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.wallet_service = WalletService(db_session)

    async def connect_wallet(self, user_id: int, wallet_address: str) -> None:
        try:
            self.wallet_service.connect_user_wallet(
                user_id=user_id,
                wallet_address=wallet_address,
            )
        except UserWalletExistError as exc:
            logger.error(str(exc))
            raise exc

        # Run initial wallet data loading
        task_result = app.send_task("fetch-wallet-details", args=(wallet_address,))
        await wait_for_task(task_result=task_result)

        redis_service = RedisService(external=True)
        redis_service.set(
            key=wallet_address,
            value="",
            ex=DEFAULT_WALLET_TRACK_EXPIRATION,
        )
        logger.info(f"User {user_id!r} connected wallet {wallet_address!r}")

    async def disconnect_wallet(self, telegram_id: int) -> None:
        user = self.user_service.get_by_telegram_id(telegram_id=telegram_id)
        telegram_chat_user_service = TelegramChatUserService(self.db_session)
        chats = telegram_chat_user_service.get_all(user_id=user.id)
        user_wallet_address = user.wallet.address
        if not chats:
            logger.debug(
                f"User {user.telegram_id!r} is not a member of any chat and won't be kicked"
            )
        else:
            telethon_service = TelethonService()
            await telethon_service.start()
            for chat in chats:
                await telethon_service.kick_chat_member(
                    chat_id=chat.chat_id,
                    telegram_user_id=user.telegram_id,
                )
                telegram_chat_user_service.delete(chat_id=chat.chat_id, user_id=user.id)
        logger.info(
            f"User {user.id!r} is disconnecting the wallet and was kicked from the group"
        )
        self.wallet_service.disconnect_user_wallet(user_id=user.id)
        logger.info(f"User {user.id!r} wallet disconnected")

        redis_service = RedisService(external=True)
        redis_service.delete(user_wallet_address)
