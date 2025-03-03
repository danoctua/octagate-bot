import logging

import sqlalchemy
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from telethon.utils import get_peer_id

from api.pos.chat import BaseTelegramChatFDO, BaseTelegramChatEligibilityRuleFDO
from core.actions.base import BaseAction
from core.dtos.chat import (
    TelegramChatJettonRuleDTO,
    TelegramChatNFTCollectionRuleDTO,
    EligibilityCheckType,
)
from core.dtos.user import TelegramUserDTO
from core.services.chat import (
    TelegramChatService,
    TelegramChatJettonService,
    TelegramChatNFTCollectionService,
    TelegramChatUserService,
)
from core.services.supertelethon import TelethonService
from core.services.user import UserService
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
        self.telegram_chat_jetton_service = TelegramChatJettonService(db_session)
        self.telegram_chat_nft_collection_service = TelegramChatNFTCollectionService(
            db_session
        )

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

    def add_jetton_rule(
        self,
        slug: str,
        address: str,
        expected: float | int,
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
                chat_id=chat.id, jetton_address=address
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
                jetton_address=address,
                threshold=expected,
            )
        )
        logger.info(f"Chat {chat.id!r} linked to jetton {address!r}")
        return BaseTelegramChatEligibilityRuleFDO(
            category=EligibilityCheckType.JETTON,
            title=new_rule.jetton.name,
            expected=new_rule.threshold,
            photo_url=new_rule.jetton.logo_path,
            blockchain_address=new_rule.jetton_address,
            is_enabled=new_rule.is_enabled,
        )

    def update_jetton_rule(
        self,
        slug: str,
        address: str,
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
                    jetton_address=address,
                    threshold=expected,
                )
            )
        except NoResultFound:
            raise HTTPException(
                detail={"error": {"message": "Rule not found"}},
                status_code=404,
            )
        return BaseTelegramChatEligibilityRuleFDO(
            category=EligibilityCheckType.JETTON,
            title=rule.jetton.name,
            expected=rule.threshold,
            photo_url=rule.jetton.logo_path,
            blockchain_address=rule.jetton_address,
            is_enabled=rule.is_enabled,
        )

    def toggle_jetton_rule(
        self,
        slug: str,
        address: str,
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
                address=address,
                is_enabled=is_enabled,
            )
        except NoResultFound:
            raise HTTPException(
                detail={"error": {"message": "Rule not found"}},
                status_code=404,
            )

        return BaseTelegramChatEligibilityRuleFDO(
            category=EligibilityCheckType.JETTON,
            title=rule.jetton.name,
            expected=rule.threshold,
            photo_url=rule.jetton.logo_path,
            blockchain_address=rule.jetton_address,
            is_enabled=rule.is_enabled,
        )

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
