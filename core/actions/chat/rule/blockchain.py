import logging

from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND

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
from core.dtos.chat.rules.toncoin import (
    CreateTelegramChatToncoinRuleDTO,
    UpdateTelegramChatToncoinRuleDTO,
)
from core.enums.jetton import CurrencyCategory
from core.enums.nft import NftCollectionAsset, NftCollectionCategoryType
from core.mappings.nft import NFT_ASSET_TO_ADDRESS_MAPPING
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
                detail="Rule not found",
                status_code=HTTP_404_NOT_FOUND,
            )
        return NftEligibilityRuleDTO.from_nft_collection_rule(rule)

    @staticmethod
    def _resolve_collection_address(
        address_raw: str, asset: NftCollectionAsset | None
    ) -> str | None:
        """
        Resolves and returns the collection address for a given raw address or asset.
        If a raw address is provided, it takes precedence and is returned as the result.
        If no raw address is provided, the function attempts to resolve the address
        using the provided `NftCollectionAsset` and a predefined mapping. If neither
        a raw address nor an asset is provided or resolvable, the function returns
        None.

        :param address_raw: The raw address string to be resolved, if available.
        :param asset: The NFT collection asset used to resolve the address when
            a raw address is not provided.
        :return: The resolved collection address as a string or None if no valid
            address could be resolved.
        """
        if address_raw:
            return address_raw

        if asset:
            return NFT_ASSET_TO_ADDRESS_MAPPING.get(asset)

        return None

    async def create(
        self,
        asset: NftCollectionAsset | None,
        address_raw: str | None,
        category: NftCollectionCategoryType | None,
        threshold: int,
    ) -> NftEligibilityRuleDTO:
        address = self._resolve_collection_address(address_raw, asset)
        if address:
            await self.nft_collection_action.get_or_create(address)

        new_rule = self.telegram_chat_nft_collection_service.create(
            CreateTelegramChatNFTCollectionRuleDTO(
                category=category,
                asset=asset,
                chat_id=self.chat.id,
                address=address,
                threshold=threshold,
                is_enabled=True,
            )
        )
        logger.info(
            f"Chat {self.chat.id!r} linked to NFT collection {address!r} and asset {asset!r}"
        )
        return NftEligibilityRuleDTO.from_nft_collection_rule(new_rule)

    async def update(
        self,
        rule_id: int,
        asset: NftCollectionAsset | None,
        address_raw: str | None,
        category: NftCollectionCategoryType | None,
        threshold: int,
        is_enabled: bool,
    ) -> NftEligibilityRuleDTO:
        try:
            rule = self.telegram_chat_nft_collection_service.get(
                rule_id, chat_id=self.chat.id
            )
        except NoResultFound:
            raise HTTPException(
                detail="Rule not found",
                status_code=HTTP_404_NOT_FOUND,
            )

        address = self._resolve_collection_address(address_raw, asset)
        if address:
            await self.nft_collection_action.get_or_create(address)

        rule = self.telegram_chat_nft_collection_service.update(
            rule=rule,
            dto=UpdateTelegramChatNFTCollectionRuleDTO(
                asset=asset,
                address=address,
                category=category,
                threshold=threshold,
                is_enabled=is_enabled,
            ),
        )
        logger.info(
            f"Updated chat nft collection rule {rule_id!r} with address {address!r} and asset {asset!r}"
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
                detail="Rule not found",
                status_code=HTTP_404_NOT_FOUND,
            )
        return ChatEligibilityRuleDTO.from_jetton_rule(rule)

    async def create(
        self,
        address_raw: str,
        category: CurrencyCategory | None,
        threshold: float | int,
    ) -> ChatEligibilityRuleDTO:
        jetton_dto = await self.jetton_action.get_or_create(address_raw)

        new_rule = self.telegram_chat_jetton_service.create(
            CreateTelegramChatJettonRuleDTO(
                chat_id=self.chat.id,
                address=jetton_dto.address,
                category=category,
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
        category: CurrencyCategory | None,
        threshold: int | float,
        is_enabled: bool,
    ) -> ChatEligibilityRuleDTO:
        try:
            rule = self.telegram_chat_jetton_service.get(rule_id, chat_id=self.chat.id)
        except NoResultFound:
            raise HTTPException(
                detail="Rule not found",
                status_code=HTTP_404_NOT_FOUND,
            )

        jetton_dto = await self.jetton_action.get_or_create(address_raw)

        updated_rule = self.telegram_chat_jetton_service.update(
            rule=rule,
            dto=UpdateTelegramChatJettonRuleDTO(
                address=jetton_dto.address,
                category=category,
                threshold=threshold,
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
                detail="Rule not found",
                status_code=HTTP_404_NOT_FOUND,
            )
        return ChatEligibilityRuleDTO.from_toncoin_rule(rule)

    def create(
        self,
        category: CurrencyCategory | None,
        threshold: float | int,
    ) -> ChatEligibilityRuleDTO:
        new_rule = self.telegram_chat_toncoin_service.create(
            CreateTelegramChatToncoinRuleDTO(
                chat_id=self.chat.id,
                category=category,
                threshold=threshold,
                is_enabled=True,
            )
        )
        logger.info(f"Chat {self.chat.id!r} linked to a new TON rule")
        return ChatEligibilityRuleDTO.from_toncoin_rule(new_rule)

    def update(
        self,
        rule_id: int,
        category: CurrencyCategory | None,
        threshold: int | float,
        is_enabled: bool,
    ) -> ChatEligibilityRuleDTO:
        try:
            rule = self.telegram_chat_toncoin_service.get(rule_id, chat_id=self.chat.id)
        except NoResultFound:
            raise HTTPException(
                detail="Rule not found",
                status_code=HTTP_404_NOT_FOUND,
            )

        updated_rule = self.telegram_chat_toncoin_service.update(
            rule=rule,
            dto=UpdateTelegramChatToncoinRuleDTO(
                category=category,
                threshold=threshold,
                is_enabled=is_enabled,
            ),
        )
        logger.info(f"Updated chat jetton rule {rule_id!r} for TON")
        return ChatEligibilityRuleDTO.from_toncoin_rule(updated_rule)

    def delete(self, rule_id: int) -> None:
        self.telegram_chat_toncoin_service.delete(rule_id, chat_id=self.chat.id)
        logger.info(f"Deleted chat TON rule {rule_id!r}")
