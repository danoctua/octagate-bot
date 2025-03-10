import logging

from pytonapi.schema.jettons import JettonInfo
from sqlalchemy.orm import Session

from core.dtos.resource import JettonDTO
from core.actions.base import BaseAction
from core.constants import JETTON_LOGO_SUB_PATH, DEFAULT_JETTON_LOGO_PATH
from core.services.jetton import JettonService
from core.services.wallet import WalletService
from core.utils.file import download_media
from wallet_indexer.indexers.tonapi import TonApiService
from wallet_indexer.tasks.wallet import fetch_wallet_details


logger = logging.getLogger(__name__)


class JettonAction(BaseAction):
    def __init__(self, db_session: Session) -> None:
        super().__init__(db_session)
        self.jetton_service = JettonService(db_session)

    async def create(self, address_raw: str) -> JettonDTO:
        blockchain_service = TonApiService()
        jetton_info: JettonInfo = await blockchain_service.get_jetton_info(address_raw)

        jetton_logo = jetton_info.metadata.image

        if jetton_logo:
            logo_name = download_media(
                jetton_logo, subdirectory=JETTON_LOGO_SUB_PATH, name=address_raw
            )
        else:
            logo_name = DEFAULT_JETTON_LOGO_PATH

        jetton = self.jetton_service.create_or_update(jetton_info, logo_path=logo_name)
        logger.info("Jetton %s created", jetton.name)

        wallet_service = WalletService(self.db_session)
        all_wallets = list(wallet_service.get_all_wallet_addresses())

        # When the new jetton is created, we need to fetch wallet details for all wallets
        # TODO: think about prioritization regular checks on events over these tasks
        logger.info("Queuing tasks for fetching wallet details")
        for wallet in all_wallets:
            fetch_wallet_details.apply_async(args=(wallet,))
        logger.info("%d tasks queued", len(all_wallets))

        return JettonDTO.from_orm(jetton)

    async def update(self, address_raw: str, is_enabled: bool) -> JettonDTO:
        jetton = self.jetton_service.update_status(address_raw, is_enabled)
        logger.info("Jetton %s updated", jetton.name)
        return JettonDTO.from_orm(jetton)
