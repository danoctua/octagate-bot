import logging

from celery.result import AsyncResult
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.orm import Session

from core.dtos.wallet import WalletDetailsWithProofDTO
from core.actions.base import BaseAction
from core.constants import (
    DEFAULT_WALLET_TRACK_EXPIRATION,
    CELERY_WALLET_FETCH_QUEUE_NAME,
    DISCONNECTED_WALLETS_SET_NAME,
)
from core.exceptions.chat import TelegramChatNotExists
from core.services.chat import TelegramChatService
from core.services.superredis import RedisService
from core.services.ton import TonProofService
from core.services.user import UserService
from core.services.wallet import (
    WalletService,
    TelegramChatUserWalletService,
)
from core.exceptions.wallet import (
    UserWalletConnectedError,
    UserWalletConnectedAnotherUserError,
    UserWalletNotConnectedError,
)
from indexer.celery_app import app

logger = logging.getLogger(__name__)


class WalletAction(BaseAction):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.wallet_service = WalletService(db_session)
        self.telegram_chat_service = TelegramChatService(db_session)
        self.telegram_chat_user_wallet_service = TelegramChatUserWalletService(
            db_session
        )
        self.user_service = UserService(db_session)

    async def connect_wallet(
        self,
        user_id: int,
        chat_slug: str,
        wallet_details: WalletDetailsWithProofDTO,
    ) -> str | None:
        """
        Connects a wallet to a user and associates it with a Telegram chat. This method performs
        several checks such as verifying the wallet's Ton proof, ensuring the wallet isn't already
        linked to a different user, and validating the existence of the Telegram chat. Additionally,
        it initiates wallet data loading, updates tracking for the wallet, and handles synchronization
        with Redis services.

        :param user_id: The unique identifier of the user to whom the wallet is being connected.
        :param chat_slug: The slug identifier representing the Telegram chat.
        :param wallet_details: An object containing wallet address and its associated proof for
            verification purposes.
        :return: A string representing the task ID of the asynchronous operation for initial wallet
            data loading if wallet did not exist in the database before. Otherwise, returns None.
        :raises UserWalletConnectedAnotherUserError: If the wallet is already connected to a different user.
        :raises TelegramChatNotExists: If no Telegram chat exists with the provided slug identifier.
        :raises UserWalletConnectedError: If the wallet is already connected to the specified chat.
        """
        TonProofService.verify_ton_proof(wallet_details=wallet_details)

        connected_wallet = self.wallet_service.get_user_wallet(
            wallet_details.wallet_address
        )
        if connected_wallet and connected_wallet.user_id != user_id:
            raise UserWalletConnectedAnotherUserError(
                f"Wallet {wallet_details.wallet_address!r} already connected to another user"
            )

        try:
            chat = self.telegram_chat_service.get_by_slug(chat_slug)
        except NoResultFound:
            raise TelegramChatNotExists(f"Chat {chat_slug!r} not found")

        if not connected_wallet:
            self.wallet_service.connect_user_wallet(
                user_id=user_id,
                wallet_address=wallet_details.wallet_address,
            )

        try:
            self.telegram_chat_user_wallet_service.connect(
                user_id=user_id,
                chat_id=chat.id,
                wallet_address=wallet_details.wallet_address,
            )
        except IntegrityError:
            raise UserWalletConnectedError(
                f"Wallet {wallet_details.wallet_address!r} already connected to chat {chat.id!r}"
            )

        # As user connected wallet, remove it from disconnected wallets set in case it was added before
        redis_service = RedisService()
        redis_service.delete_from_set(DISCONNECTED_WALLETS_SET_NAME, str(user_id))

        task_id = None
        if not connected_wallet:
            # Run initial wallet data loading
            task_result: AsyncResult = app.send_task(
                "fetch-wallet-details",
                args=(wallet_details.wallet_address,),
                queue=CELERY_WALLET_FETCH_QUEUE_NAME,
            )
            # Add wallet to tracking
            redis_external_service = RedisService(external=True)
            redis_external_service.set(
                key=wallet_details.wallet_address,
                value="",
                ex=DEFAULT_WALLET_TRACK_EXPIRATION,
            )
            task_id = task_result.task_id

        logger.info(
            f"User {user_id!r} connected wallet {wallet_details.wallet_address!r}"
        )
        return task_id

    async def disconnect_wallet(self, user_id: int, chat_slug: str) -> None:
        """
        Disconnects a wallet associated with a user from a specific Telegram chat. If the chat
        with the given chat_slug does not exist, an exception is raised. This method also performs a
        cleanup by removing the wallet mapping and updating the Redis set to reflect the disconnected
        status. Finally, it logs the operation for tracking purposes.

        WARNING: It doesn't remove the UserWallet link

        :param user_id: The unique identifier of the user whose wallet needs to be disconnected.
        :param chat_slug: The unique slug identifier of the Telegram chat from which the user's wallet
            is being disconnected.
        :raises TelegramChatNotExists: If no chat exists with the provided slug identifier.
        """
        try:
            chat = self.telegram_chat_service.get_by_slug(chat_slug)
        except NoResultFound:
            raise TelegramChatNotExists(f"Chat {chat_slug!r} not found")

        # Remove user wallet mapping
        self.telegram_chat_user_wallet_service.disconnect(
            chat_id=chat.id,
            user_id=user_id,
        )

        redis_service = RedisService()
        redis_service.add_to_set(DISCONNECTED_WALLETS_SET_NAME, str(user_id))
        logger.info(f"User {user_id!r} disconnected wallet from chat {chat.id!r}")

    async def set_wallet(
        self, user_id: int, chat_slug: str, wallet_address: str
    ) -> None:
        """
        Sets a wallet for a user in a specified chat by connecting the wallet address to the
        user within the chat.

        This method handles the process of associating a wallet address with a user for a
        specific Telegram chat. It validates whether the wallet address is already connected
        to the user. If the specified chat does not exist, it raises an exception. Once the
        validations pass, the wallet is successfully connected, and a record of the action
        is logged.

        :param user_id: The unique identifier of the user.
        :param chat_slug: The unique slug identifier of the chat.
        :param wallet_address: The wallet address to be set for the user.

        :raises TelegramChatNotExists: If no chat exists with the provided slug identifier.
        :raises UserWalletNotConnectedError: If the wallet is already connected to the specified chat.
        """
        connected_wallet = self.wallet_service.get_user_wallet(
            wallet_address=wallet_address, user_id=user_id
        )
        if not connected_wallet:
            logger.warning(
                f"User {user_id!r} tried to connect wallet {wallet_address!r} that wasn't connected by user. Ignoring."
            )
            raise UserWalletNotConnectedError(
                f"Wallet {wallet_address!r} was not connected by user"
            )

        try:
            chat = self.telegram_chat_service.get_by_slug(chat_slug)
        except NoResultFound:
            raise TelegramChatNotExists(f"Chat {chat_slug!r} not found")

        self.telegram_chat_user_wallet_service.connect(
            user_id=user_id,
            chat_id=chat.id,
            wallet_address=wallet_address,
        )
        logger.info(
            f"User {user_id!r} set wallet {wallet_address!r} for chat {chat.id!r}"
        )
