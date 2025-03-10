import logging

from celery.result import AsyncResult
from sqlalchemy.orm import Session

from core.dtos.wallet import WalletDetailsWithProofDTO
from core.actions.base import BaseAction
from core.constants import (
    DEFAULT_WALLET_TRACK_EXPIRATION,
    CELERY_WALLET_FETCH_QUEUE_NAME,
    DISCONNECTED_WALLETS_SET_NAME,
)
from core.services.superredis import RedisService
from core.services.ton import TonProofService
from core.services.wallet import (
    WalletService,
)
from core.exceptions.wallet import UserWalletExistError, UserWalletConnectedError
from wallet_indexer.celery_app import app

logger = logging.getLogger(__name__)


class WalletAction(BaseAction):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.wallet_service = WalletService(db_session)

    async def connect_wallet(
        self,
        user_id: int,
        wallet_details: WalletDetailsWithProofDTO,
    ) -> str:
        TonProofService.verify_ton_proof(wallet_details=wallet_details)
        try:
            self.wallet_service.connect_user_wallet(
                user_id=user_id,
                wallet_address=wallet_details.wallet_address,
            )
        except UserWalletExistError as exc:
            logger.error(str(exc))
            raise exc

        except UserWalletConnectedError as exc:
            logger.error(str(exc))
            raise exc

        # Run initial wallet data loading
        task_result: AsyncResult = app.send_task(
            "fetch-wallet-details",
            args=(wallet_details.wallet_address,),
            queue=CELERY_WALLET_FETCH_QUEUE_NAME,
        )
        # As user connected wallet, remove it from disconnected wallets set in case it was added before
        redis_service = RedisService()
        redis_service.delete_from_set(DISCONNECTED_WALLETS_SET_NAME, str(user_id))
        # Add wallet to tracking
        redis_external_service = RedisService(external=True)
        redis_external_service.set(
            key=wallet_details.wallet_address,
            value="",
            ex=DEFAULT_WALLET_TRACK_EXPIRATION,
        )
        logger.info(
            f"User {user_id!r} connected wallet {wallet_details.wallet_address!r}"
        )
        return task_result.task_id

    async def disconnect_wallet(self, telegram_id: int) -> None:
        user = self.user_service.get_by_telegram_id(telegram_id=telegram_id)
        user_wallet_address = user.wallet.address
        # Add user to disconnected wallets set to validate and kick from the chats
        # where the user is a member and is not eligible anymore
        redis_service = RedisService()
        redis_service.add_to_set(DISCONNECTED_WALLETS_SET_NAME, str(user.id))
        # Remove user wallet mapping
        self.wallet_service.disconnect_user_wallet(user_id=user.id)
        logger.info(f"User {user.id!r} wallet disconnected")
        # Remove wallet from tracking
        redis_external_service = RedisService(external=True)
        redis_external_service.delete(user_wallet_address)
