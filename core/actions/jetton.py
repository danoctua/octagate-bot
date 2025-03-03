import logging

from pytonapi.schema.jettons import JettonInfo
from sqlalchemy.orm import Session

from api.pos.ton import JettonFDO
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

    async def create(self, jetton_address: str) -> JettonFDO:
        blockchain_service = TonApiService()
        jetton_info: JettonInfo = await blockchain_service.get_jetton_info(
            jetton_address
        )

        jetton_logo = jetton_info.metadata.image

        if jetton_logo:
            logo_name = download_media(
                jetton_logo, subdirectory=JETTON_LOGO_SUB_PATH, name=jetton_address
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

        return JettonFDO(
            address=jetton.address,
            name=jetton.name,
            description=jetton.description,
            symbol=jetton.symbol,
            logo_path=jetton.logo_path,
            is_enabled=jetton.is_enabled,
        )

    async def update(self, jetton_address: str, is_enabled: bool) -> JettonFDO:
        jetton = self.jetton_service.update_status(jetton_address, is_enabled)
        logger.info("Jetton %s updated", jetton.name)
        return JettonFDO(
            address=jetton.address,
            name=jetton.name,
            description=jetton.description,
            symbol=jetton.symbol,
            logo_path=jetton.logo_path,
            is_enabled=jetton.is_enabled,
        )
