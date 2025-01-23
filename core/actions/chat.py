import logging

from sqlalchemy.orm import Session

from core.actions.base import BaseAction
from core.dtos.chat import TelegramChatJettonRuleDTO, TelegramChatNFTCollectionRuleDTO
from core.services.chat import (
    TelegramChatService,
    TelegramChatJettonService,
    TelegramChatNFTCollectionService,
)

logger = logging.getLogger(__name__)


class TelegramChatAction(BaseAction):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.telegram_chat_service = TelegramChatService(db_session)
        self.telegram_chat_jetton_service = TelegramChatJettonService(db_session)
        self.telegram_chat_nft_collection_service = TelegramChatNFTCollectionService(
            db_session
        )

    def add_jetton_rule(
        self,
        dto: TelegramChatJettonRuleDTO,
    ) -> None:
        telegram_chat_jetton_service = TelegramChatJettonService(self.db_session)
        telegram_chat_jetton_service.create(dto)

        logger.info(f"Chat {dto.chat_id!r} linked to jetton {dto.jetton_address!r}")

    def add_nft_collection_rule(
        self,
        dto: TelegramChatNFTCollectionRuleDTO,
    ) -> None:
        telegram_chat_nft_collection_service = TelegramChatNFTCollectionService(
            self.db_session
        )
        telegram_chat_nft_collection_service.create(dto)

        logger.info(
            f"Chat {dto.chat_id!r} linked to NFT collection {dto.collection_address!r}"
        )
