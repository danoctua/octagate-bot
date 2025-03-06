import logging

import sqlalchemy
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from telethon.utils import get_peer_id

from api.pos.chat import (
    BaseTelegramChatFDO,
    BaseTelegramChatEligibilityRuleFDO,
    TelegramChatWithRulesFDO,
    TelegramChatFDO,
    TelegramChatEligibilityRuleFDO,
)
from core.actions.base import BaseAction
from core.dtos.chat import (
    TelegramChatJettonRuleDTO,
    TelegramChatNFTCollectionRuleDTO,
    TelegramChatEligibilitySummaryDTO,
)
from core.dtos.user import TelegramUserDTO
from core.models.user import User
from core.services.chat import (
    TelegramChatService,
    TelegramChatJettonService,
    TelegramChatNFTCollectionService,
    TelegramChatUserService,
)
from core.services.nft import NftItemService
from core.services.supertelethon import TelethonService
from core.services.user import UserService
from core.services.wallet import JettonWalletService
from core.settings import core_settings

logger = logging.getLogger(__name__)


class TelegramChatNotSufficientPrivileges(Exception):
    pass


class TelegramChatAlreadyExists(Exception):
    pass


class TelegramChatNotExists(Exception):
    pass


class TelegramChatAction(BaseAction):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.telegram_chat_service = TelegramChatService(db_session)
        self.telegram_chat_user_service = TelegramChatUserService(db_session)

    async def create(self, chat_identifier: str | int) -> BaseTelegramChatFDO:
        telethon_service = TelethonService()
        await telethon_service.start()

        logger.info(f"Loading chat {chat_identifier!r}...")

        try:
            chat = await telethon_service.get_chat(chat_identifier)
        except ValueError as e:
            logger.error(f"Chat {chat_identifier!r} not found", exc_info=e)
            raise TelegramChatNotExists(f"Chat {chat_identifier!r} not found")

        if not chat.admin_rights or not all([chat.admin_rights.invite_users]):
            logger.error(f"Bot user has no rights to invite users: {chat_identifier!r}")
            raise TelegramChatNotSufficientPrivileges(
                f"Bot user has no rights to change chat info: {chat_identifier!r}"
            )

        logo_path = await telethon_service.download_profile_photo(chat)
        try:
            telegram_chat = self.telegram_chat_service.create(
                chat_id=get_peer_id(chat, add_mark=True),
                entity=chat,
                logo_path=logo_path,
            )
        except sqlalchemy.exc.IntegrityError:
            logger.error(f"Chat {chat_identifier!r} already exists")
            raise TelegramChatAlreadyExists(f"Chat {chat_identifier!r} already exists")

        if not telegram_chat.invite_link:
            logger.info(
                f"Creating chat invite link for new chat {chat_identifier!r}..."
            )
            invite_link = await telethon_service.get_invite_link(chat)
            self.telegram_chat_service.refresh_invite_link(
                chat_identifier, invite_link.link
            )
        else:
            logger.info(
                f"Chat invite link for new chat {chat_identifier!r} already exists..."
            )

        user_service = UserService(self.db_session)
        logger.info(f"Loading chat participants or chat {chat_identifier!r}...")

        chat_participants_count = 0
        async for participant_user in telethon_service.get_participants(
            chat_identifier
        ):
            if participant_user.bot:
                continue

            user = user_service.create_or_update(
                TelegramUserDTO(
                    id=participant_user.id,
                    first_name=participant_user.first_name or "",
                    last_name=participant_user.last_name,
                    username=participant_user.username,
                    is_premium=participant_user.premium or False,
                    language_code=participant_user.lang_code
                    or core_settings.default_language,
                )
            )
            self.telegram_chat_user_service.create_or_update(
                chat_id=chat_identifier,
                user_id=user.id,
                is_admin=hasattr(participant_user.participant, "admin_rights"),
                is_whale_admin=False,
            )
            chat_participants_count += 1

        logger.info(f"Chat {chat_identifier!r} loaded successfully")
        return BaseTelegramChatFDO(
            id=telegram_chat.id,
            username=telegram_chat.username,
            title=telegram_chat.title,
            description=telegram_chat.description,
            slug=telegram_chat.slug,
            is_forum=telegram_chat.is_forum,
            logo_path=telegram_chat.logo_path,
        )

    async def get_with_eligibility_summary(
        self, slug: str, user: User
    ) -> TelegramChatWithRulesFDO:
        """
        This is non-administrative method to get chat with rules
        :param slug:
        :param user:
        :return:
        :raises TelegramChatNotExists: if chat with slug not found
        """
        try:
            chat = self.telegram_chat_service.get_by_slug(slug)
        except NoResultFound:
            logger.error(f"Chat with slug {slug!r} not found")
            raise TelegramChatNotExists(f"Chat with slug {slug!r} not found")
        eligibility_rules = self.telegram_chat_user_service.get_eligibility_rules(
            chat_id=chat.id,
            enabled_only=True,
        )

        if user.wallet:
            nft_item_service = NftItemService(self.db_session)
            user_nft_items = nft_item_service.get_all(owner_address=user.wallet.address)
            jetton_wallet_service = JettonWalletService(self.db_session)
            user_jettons = jetton_wallet_service.get_all(
                owner_address=user.wallet.address
            )
        else:
            user_nft_items = []
            user_jettons = []

        eligibility_summary: TelegramChatEligibilitySummaryDTO = (
            self.telegram_chat_user_service.is_user_eligible_chat_member(
                eligibility_rules=eligibility_rules,
                user_jettons=user_jettons,
                user_nft_items=user_nft_items,
                chat_member=None,
            )
        )
        is_chat_member = self.telegram_chat_user_service.is_chat_member(
            chat_id=chat.id,
            user_id=user.id,
        )
        is_eligible = bool(eligibility_summary)

        return TelegramChatWithRulesFDO(
            chat=TelegramChatFDO(
                id=chat.id,
                username=chat.username,
                title=chat.title,
                description=chat.description,
                slug=chat.slug,
                is_forum=chat.is_forum,
                logo_path=chat.logo_path,
                join_url=chat.invite_link if is_eligible else None,
                is_member=is_chat_member,
                is_eligible=is_eligible,
            ),
            rules=[
                TelegramChatEligibilityRuleFDO(
                    category=rule.category,
                    title=rule.title,
                    expected=rule.expected,
                    actual=rule.current,
                    is_eligible=rule.is_eligible,
                    photo_url=None,
                    blockchain_address=rule.address,
                    is_enabled=rule.is_enabled,
                )
                for rule in eligibility_summary.items
            ],
        )

    async def get_with_eligibility_rules(self, slug: str) -> TelegramChatWithRulesFDO:
        try:
            chat = self.telegram_chat_service.get_by_slug(slug)
        except NoResultFound:
            logger.error(f"Chat with slug {slug!r} not found")
            raise TelegramChatNotExists(f"Chat with slug {slug!r} not found")
        eligibility_rules = self.telegram_chat_user_service.get_eligibility_rules(
            chat_id=chat.id,
            enabled_only=False,
        )

        return TelegramChatWithRulesFDO(
            chat=TelegramChatFDO(
                id=chat.id,
                username=chat.username,
                title=chat.title,
                description=chat.description,
                slug=chat.slug,
                is_forum=chat.is_forum,
                logo_path=chat.logo_path,
                join_url=chat.invite_link,
                is_member=False,
                is_eligible=False,
            ),
            rules=[
                *(
                    TelegramChatEligibilityRuleFDO.from_jetton_rule(rule)
                    for rule in eligibility_rules.jettons
                ),
                *(
                    TelegramChatEligibilityRuleFDO.from_nft_collection_rule(rule)
                    for rule in eligibility_rules.nft_collections
                ),
            ],
        )


class TelegramChatNFTCollectionAction(BaseAction):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.telegram_chat_service = TelegramChatService(db_session)
        self.telegram_chat_nft_collection_service = TelegramChatNFTCollectionService(
            db_session
        )

    def read(
        self,
        slug: str,
        address_raw: str,
    ) -> BaseTelegramChatEligibilityRuleFDO:
        chat = self.telegram_chat_service.get_by_slug(slug)
        rule = self.telegram_chat_nft_collection_service.get(
            chat_id=chat.id, collection_address=address_raw
        )
        return BaseTelegramChatEligibilityRuleFDO.from_nft_collection_rule(rule)

    def create(
        self,
        slug: str,
        address_raw: str,
        threshold: int,
    ) -> BaseTelegramChatEligibilityRuleFDO:
        chat = self.telegram_chat_service.get_by_slug(slug)
        new_rule = self.telegram_chat_nft_collection_service.create(
            TelegramChatNFTCollectionRuleDTO(
                chat_id=chat.id,
                address=address_raw,
                threshold=threshold,
            )
        )
        logger.info(f"Chat {chat.id!r} linked to NFT collection {address_raw!r}")
        return BaseTelegramChatEligibilityRuleFDO.from_nft_collection_rule(new_rule)

    def update(
        self,
        slug: str,
        address: str,
        expected: int,
    ) -> BaseTelegramChatEligibilityRuleFDO:
        chat = self.telegram_chat_service.get_by_slug(slug)
        rule = self.telegram_chat_nft_collection_service.update(
            TelegramChatNFTCollectionRuleDTO(
                chat_id=chat.id,
                address=address,
                threshold=expected,
            )
        )
        return BaseTelegramChatEligibilityRuleFDO.from_nft_collection_rule(rule)


class TelegramChatJettonAction(BaseAction):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.telegram_chat_service = TelegramChatService(db_session)
        self.telegram_chat_jetton_service = TelegramChatJettonService(db_session)

    def create(
        self,
        slug: str,
        address_raw: str,
        threshold: float | int,
    ) -> BaseTelegramChatEligibilityRuleFDO:
        try:
            chat = self.telegram_chat_service.get_by_slug(slug)
        except NoResultFound:
            logger.debug(f"Chat with slug {slug!r} not found")
            raise HTTPException(
                detail={"error": {"message": "Chat not found"}},
                status_code=404,
            )

        try:
            self.telegram_chat_jetton_service.get(
                chat_id=chat.id, jetton_address=address_raw
            )
            raise HTTPException(
                detail={"error": {"message": "Rule already exists"}},
                status_code=409,
            )
        except NoResultFound:
            pass

        new_rule = self.telegram_chat_jetton_service.create(
            TelegramChatJettonRuleDTO(
                chat_id=chat.id,
                address=address_raw,
                threshold=threshold,
            )
        )
        logger.info(f"Chat {chat.id!r} linked to jetton {address_raw!r}")
        return BaseTelegramChatEligibilityRuleFDO.from_jetton_rule(new_rule)

    def update(
        self,
        slug: str,
        address_raw: str,
        expected: int | float,
    ) -> BaseTelegramChatEligibilityRuleFDO:
        try:
            chat = self.telegram_chat_service.get_by_slug(slug)
        except NoResultFound:
            logger.debug(f"Chat with slug {slug!r} not found")
            raise HTTPException(
                detail={"error": {"message": "Chat not found"}},
                status_code=404,
            )
        try:
            rule = self.telegram_chat_jetton_service.update(
                TelegramChatJettonRuleDTO(
                    chat_id=chat.id,
                    address=address_raw,
                    threshold=expected,
                )
            )
        except NoResultFound:
            raise HTTPException(
                detail={"error": {"message": "Rule not found"}},
                status_code=404,
            )
        return BaseTelegramChatEligibilityRuleFDO.from_jetton_rule(rule)

    def toggle(
        self,
        slug: str,
        address_raw: str,
        is_enabled: bool,
    ) -> BaseTelegramChatEligibilityRuleFDO:
        try:
            chat = self.telegram_chat_service.get_by_slug(slug)
        except NoResultFound:
            logger.debug(f"Chat with slug {slug!r} not found")
            raise HTTPException(
                detail={"error": {"message": "Chat not found"}},
                status_code=404,
            )

        try:
            rule = self.telegram_chat_jetton_service.toggle_rule(
                chat_id=chat.id,
                address=address_raw,
                is_enabled=is_enabled,
            )
        except NoResultFound:
            raise HTTPException(
                detail={"error": {"message": "Rule not found"}},
                status_code=404,
            )

        return BaseTelegramChatEligibilityRuleFDO.from_jetton_rule(rule)
