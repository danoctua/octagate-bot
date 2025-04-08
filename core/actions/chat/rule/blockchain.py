import logging

from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from core.actions.chat.base import ManagedChatBaseAction
from core.actions.jetton import JettonAction
from core.actions.nft_collection import NftCollectionAction
from core.dtos.chat.rules import ChatEligibilityRuleDTO
from core.dtos.chat.rules.nft import (
    CreateTelegramChatNFTCollectionRuleDTO,
    NftEligibilityRuleDTO,
    UpdateTelegramChatNFTCollectionRuleDTO,
)
from core.dtos.chat.rules.jetton import (
    CreateTelegramChatJettonRuleDTO,
    UpdateTelegramChatJettonRuleDTO,
)
from core.dtos.base import NftItemAttributeDTO
from core.dtos.chat.rules.toncoin import (
    CreateTelegramChatToncoinRuleDTO,
    UpdateTelegramChatToncoinRuleDTO,
)
from core.models.user import User
from core.services.chat.rule.blockchain import (
    TelegramChatNFTCollectionService,
    TelegramChatJettonService,
    TelegramChatToncoinService,
)

logger = logging.getLogger(__name__)


class TelegramChatNFTCollectionAction(ManagedChatBaseAction):
    def __init__(self, db_session: Session, requestor: User, chat_slug: str) -> None:
        super().__init__(
            db_session=db_session, requestor=requestor, chat_slug=chat_slug
        )
        self.telegram_chat_nft_collection_service = TelegramChatNFTCollectionService(
            db_session
        )
        self.nft_collection_action = NftCollectionAction(db_session)

    def read(self, rule_id: int) -> NftEligibilityRuleDTO:
        try:
            rule = self.telegram_chat_nft_collection_service.get(
                rule_id, chat_id=self.chat.id
            )
        except NoResultFound:
            raise HTTPException(
                detail={"error": {"message": "Rule not found"}},
                status_code=404,
            )
        return NftEligibilityRuleDTO.from_nft_collection_rule(rule)

    async def create(
        self,
        address_raw: str,
        threshold: int,
        required_attributes: list[NftItemAttributeDTO] | None,
    ) -> NftEligibilityRuleDTO:
        nft_collection = await self.nft_collection_action.get_or_create(address_raw)

        new_rule = self.telegram_chat_nft_collection_service.create(
            CreateTelegramChatNFTCollectionRuleDTO(
                chat_id=self.chat.id,
                address=nft_collection.address,
                threshold=threshold,
                is_enabled=True,
                required_attributes=required_attributes,
            )
        )
        logger.info(f"Chat {self.chat.id!r} linked to NFT collection {address_raw!r}")
        return NftEligibilityRuleDTO.from_nft_collection_rule(new_rule)

    async def update(
        self,
        rule_id: int,
        address_raw: str,
        expected: int,
        is_enabled: bool,
        required_attributes: list[NftItemAttributeDTO] | None,
    ) -> NftEligibilityRuleDTO:
        try:
            rule = self.telegram_chat_nft_collection_service.get(
                rule_id, chat_id=self.chat.id
            )
        except NoResultFound:
            raise HTTPException(
                detail={"error": {"message": "Rule not found"}},
                status_code=404,
            )
        rule = self.telegram_chat_nft_collection_service.update(
            rule=rule,
            dto=UpdateTelegramChatNFTCollectionRuleDTO(
                address=address_raw,
                threshold=expected,
                is_enabled=is_enabled,
                required_attributes=required_attributes,
            ),
        )
        return NftEligibilityRuleDTO.from_nft_collection_rule(rule)

    async def delete(self, rule_id: int) -> None:
        self.telegram_chat_nft_collection_service.delete(rule_id, chat_id=self.chat.id)
        logger.info(f"Deleted chat nft collection rule {rule_id!r}")


class TelegramChatJettonAction(ManagedChatBaseAction):
    def __init__(self, db_session: Session, requestor: User, chat_slug: str) -> None:
        super().__init__(
            db_session=db_session, requestor=requestor, chat_slug=chat_slug
        )
        self.telegram_chat_jetton_service = TelegramChatJettonService(db_session)
        self.jetton_action = JettonAction(db_session)

    def read(self, rule_id: int) -> ChatEligibilityRuleDTO:
        try:
            rule = self.telegram_chat_jetton_service.get(rule_id, chat_id=self.chat.id)
        except NoResultFound:
            raise HTTPException(
                detail={"error": {"message": "Rule not found"}},
                status_code=404,
            )
        return ChatEligibilityRuleDTO.from_jetton_rule(rule)

    async def create(
        self,
        address_raw: str,
        threshold: float | int,
    ) -> ChatEligibilityRuleDTO:
        jetton_dto = await self.jetton_action.get_or_create(address_raw)

        new_rule = self.telegram_chat_jetton_service.create(
            CreateTelegramChatJettonRuleDTO(
                chat_id=self.chat.id,
                address=jetton_dto.address,
                threshold=threshold,
                is_enabled=True,
            )
        )
        logger.info(f"Chat {self.chat.id!r} linked to jetton {jetton_dto.address!r}")
        return ChatEligibilityRuleDTO.from_jetton_rule(new_rule)

    async def update(
        self,
        rule_id: int,
        address_raw: str,
        expected: int | float,
        is_enabled: bool,
    ) -> ChatEligibilityRuleDTO:
        try:
            rule = self.telegram_chat_jetton_service.get(rule_id, chat_id=self.chat.id)
        except NoResultFound:
            raise HTTPException(
                detail={"error": {"message": "Rule not found"}},
                status_code=404,
            )

        jetton_dto = await self.jetton_action.get_or_create(address_raw)

        updated_rule = self.telegram_chat_jetton_service.update(
            rule=rule,
            dto=UpdateTelegramChatJettonRuleDTO(
                address=jetton_dto.address,
                threshold=expected,
                is_enabled=is_enabled,
            ),
        )
        logger.info(
            f"Updated chat jetton rule {rule_id!r} with address {jetton_dto.address!r}"
        )
        return ChatEligibilityRuleDTO.from_jetton_rule(updated_rule)

    async def delete(self, rule_id: int) -> None:
        self.telegram_chat_jetton_service.delete(rule_id, chat_id=self.chat.id)
        logger.info(f"Deleted chat jetton rule {rule_id!r}")


class TelegramChatToncoinAction(ManagedChatBaseAction):
    def __init__(self, db_session: Session, requestor: User, chat_slug: str) -> None:
        super().__init__(
            db_session=db_session, requestor=requestor, chat_slug=chat_slug
        )
        self.telegram_chat_toncoin_service = TelegramChatToncoinService(db_session)

    def read(self, rule_id: int) -> ChatEligibilityRuleDTO:
        try:
            rule = self.telegram_chat_toncoin_service.get(rule_id, chat_id=self.chat.id)
        except NoResultFound:
            raise HTTPException(
                detail={"error": {"message": "Rule not found"}},
                status_code=404,
            )
        return ChatEligibilityRuleDTO.from_toncoin_rule(rule)

    def create(
        self,
        threshold: float | int,
    ) -> ChatEligibilityRuleDTO:
        new_rule = self.telegram_chat_toncoin_service.create(
            CreateTelegramChatToncoinRuleDTO(
                chat_id=self.chat.id,
                threshold=threshold,
                is_enabled=True,
            )
        )
        logger.info(f"Chat {self.chat.id!r} linked to a new TON rule")
        return ChatEligibilityRuleDTO.from_toncoin_rule(new_rule)

    def update(
        self,
        rule_id: int,
        threshold: int | float,
        is_enabled: bool,
    ) -> ChatEligibilityRuleDTO:
        try:
            rule = self.telegram_chat_toncoin_service.get(rule_id, chat_id=self.chat.id)
        except NoResultFound:
            raise HTTPException(
                detail={"error": {"message": "Rule not found"}},
                status_code=404,
            )

        updated_rule = self.telegram_chat_toncoin_service.update(
            rule=rule,
            dto=UpdateTelegramChatToncoinRuleDTO(
                threshold=threshold,
                is_enabled=is_enabled,
            ),
        )
        logger.info(f"Updated chat jetton rule {rule_id!r} for TON")
        return ChatEligibilityRuleDTO.from_toncoin_rule(updated_rule)

    def delete(self, rule_id: int) -> None:
        self.telegram_chat_toncoin_service.delete(rule_id, chat_id=self.chat.id)
        logger.info(f"Deleted chat TON rule {rule_id!r}")
