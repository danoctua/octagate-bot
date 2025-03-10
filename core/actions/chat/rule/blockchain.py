import logging

from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from core.actions.base import BaseAction
from core.dtos.chat import (
    CreateTelegramChatNFTCollectionRuleDTO,
    CreateTelegramChatJettonRuleDTO,
    BaseTelegramChatEligibilityRuleDTO,
)
from core.services.chat import TelegramChatService
from core.services.chat.rule.blockchain import (
    TelegramChatNFTCollectionService,
    TelegramChatJettonService,
)


logger = logging.getLogger(__name__)


class TelegramChatNFTCollectionAction(BaseAction):
    def __init__(self, db_session: Session) -> None:
        super().__init__(db_session)
        self.telegram_chat_service = TelegramChatService(db_session)
        self.telegram_chat_nft_collection_service = TelegramChatNFTCollectionService(
            db_session
        )

    def read(self, rule_id: int) -> BaseTelegramChatEligibilityRuleDTO:
        try:
            rule = self.telegram_chat_nft_collection_service.get(rule_id)
        except NoResultFound:
            raise HTTPException(
                detail={"error": {"message": "Rule not found"}},
                status_code=404,
            )
        return BaseTelegramChatEligibilityRuleDTO.from_nft_collection_rule(rule)

    def create(
        self,
        slug: str,
        address_raw: str,
        threshold: int,
    ) -> BaseTelegramChatEligibilityRuleDTO:
        try:
            chat = self.telegram_chat_service.get_by_slug(slug)
        except NoResultFound:
            logger.debug(f"Chat with slug {slug!r} not found")
            raise HTTPException(
                detail={"error": {"message": "Chat not found"}},
                status_code=404,
            )
        new_rule = self.telegram_chat_nft_collection_service.create(
            CreateTelegramChatNFTCollectionRuleDTO(
                chat_id=chat.id,
                address=address_raw,
                threshold=threshold,
                is_enabled=True,
            )
        )
        logger.info(f"Chat {chat.id!r} linked to NFT collection {address_raw!r}")
        return BaseTelegramChatEligibilityRuleDTO.from_nft_collection_rule(new_rule)

    def update(
        self,
        rule_id: int,
        address_raw: str,
        expected: int,
        is_enabled: bool,
    ) -> BaseTelegramChatEligibilityRuleDTO:
        try:
            rule = self.telegram_chat_nft_collection_service.update(
                rule_id=rule_id,
                address=address_raw,
                threshold=expected,
                is_enabled=is_enabled,
            )
        except NoResultFound:
            raise HTTPException(
                detail={"error": {"message": "Rule not found"}},
                status_code=404,
            )
        return BaseTelegramChatEligibilityRuleDTO.from_nft_collection_rule(rule)


class TelegramChatJettonAction(BaseAction):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.telegram_chat_service = TelegramChatService(db_session)
        self.telegram_chat_jetton_service = TelegramChatJettonService(db_session)

    def read(self, rule_id: int) -> BaseTelegramChatEligibilityRuleDTO:
        try:
            rule = self.telegram_chat_jetton_service.get(rule_id)
        except NoResultFound:
            raise HTTPException(
                detail={"error": {"message": "Rule not found"}},
                status_code=404,
            )
        return BaseTelegramChatEligibilityRuleDTO.from_jetton_rule(rule)

    def create(
        self,
        slug: str,
        address_raw: str,
        threshold: float | int,
    ) -> BaseTelegramChatEligibilityRuleDTO:
        try:
            chat = self.telegram_chat_service.get_by_slug(slug)
        except NoResultFound:
            logger.debug(f"Chat with slug {slug!r} not found")
            raise HTTPException(
                detail={"error": {"message": "Chat not found"}},
                status_code=404,
            )

        new_rule = self.telegram_chat_jetton_service.create(
            CreateTelegramChatJettonRuleDTO(
                chat_id=chat.id,
                address=address_raw,
                threshold=threshold,
                is_enabled=True,
            )
        )
        logger.info(f"Chat {chat.id!r} linked to jetton {address_raw!r}")
        return BaseTelegramChatEligibilityRuleDTO.from_jetton_rule(new_rule)

    def update(
        self,
        rule_id: int,
        address_raw: str,
        expected: int | float,
        is_enabled: bool,
    ) -> BaseTelegramChatEligibilityRuleDTO:
        try:
            rule = self.telegram_chat_jetton_service.update(
                rule_id=rule_id,
                address=address_raw,
                threshold=expected,
                is_enabled=is_enabled,
            )
        except NoResultFound:
            raise HTTPException(
                detail={"error": {"message": "Rule not found"}},
                status_code=404,
            )
        return BaseTelegramChatEligibilityRuleDTO.from_jetton_rule(rule)
