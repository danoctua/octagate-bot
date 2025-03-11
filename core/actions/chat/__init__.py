import logging

import sqlalchemy
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from telethon.utils import get_peer_id

from core.dtos.chat import (
    BaseTelegramChatDTO,
    TelegramChatDTO,
    TelegramChatWithRulesDTO,
    TelegramChatEligibilityRuleDTO,
)
from core.actions.authorization import AuthorizationAction
from core.actions.base import BaseAction
from core.exceptions.chat import (
    TelegramChatNotSufficientPrivileges,
    TelegramChatAlreadyExists,
    TelegramChatNotExists,
)
from core.dtos.user import TelegramUserDTO
from core.models.user import User
from core.services.chat import TelegramChatService
from core.services.chat.user import TelegramChatUserService
from core.services.supertelethon import TelethonService
from core.services.user import UserService
from core.settings import core_settings


logger = logging.getLogger(__name__)


class TelegramChatAction(BaseAction):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.telegram_chat_service = TelegramChatService(db_session)
        self.telegram_chat_user_service = TelegramChatUserService(db_session)
        self.authorization_action = AuthorizationAction(db_session)

    async def create(self, chat_identifier: str | int) -> BaseTelegramChatDTO:
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
            )
            chat_participants_count += 1

        logger.info(f"Chat {chat_identifier!r} loaded successfully")
        return BaseTelegramChatDTO(
            id=telegram_chat.id,
            username=telegram_chat.username,
            title=telegram_chat.title,
            description=telegram_chat.description,
            slug=telegram_chat.slug,
            is_forum=telegram_chat.is_forum,
            logo_path=telegram_chat.logo_path,
        )

    async def update(self, slug: str, description: str | None) -> BaseTelegramChatDTO:
        try:
            chat = self.telegram_chat_service.get_by_slug(slug)
        except NoResultFound:
            logger.error(f"Chat with slug {slug!r} not found")
            raise TelegramChatNotExists(f"Chat with slug {slug!r} not found")

        self.telegram_chat_service.update_description(
            chat=chat,
            description=description,
        )

        return BaseTelegramChatDTO(
            id=chat.id,
            username=chat.username,
            title=chat.title,
            description=chat.description,
            slug=chat.slug,
            is_forum=chat.is_forum,
            logo_path=chat.logo_path,
        )

    async def get_with_eligibility_summary(
        self, slug: str, user: User
    ) -> TelegramChatWithRulesDTO:
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
        eligibility_summary = self.authorization_action.is_user_eligible_chat_member(
            chat_id=chat.id,
            user_id=user.id,
        )
        is_chat_member = self.telegram_chat_user_service.is_chat_member(
            chat_id=chat.id,
            user_id=user.id,
        )
        is_eligible = bool(eligibility_summary)

        return TelegramChatWithRulesDTO(
            chat=TelegramChatDTO(
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
                TelegramChatEligibilityRuleDTO(
                    id=rule.id,
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

    async def get_with_eligibility_rules(self, slug: str) -> TelegramChatWithRulesDTO:
        """
        This is administrative method to get chat with rules that includes disabled rules
        :param slug: slug of chat for which data is requested
        :return: DTO with chat and rules
        """
        try:
            chat = self.telegram_chat_service.get_by_slug(slug)
        except NoResultFound:
            logger.error(f"Chat with slug {slug!r} not found")
            raise TelegramChatNotExists(f"Chat with slug {slug!r} not found")
        eligibility_rules = self.authorization_action.get_eligibility_rules(
            chat_id=chat.id,
            enabled_only=False,
        )

        return TelegramChatWithRulesDTO(
            chat=TelegramChatDTO(
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
            rules=sorted(
                [
                    *(
                        TelegramChatEligibilityRuleDTO.from_jetton_rule(rule)
                        for rule in eligibility_rules.jettons
                    ),
                    *(
                        TelegramChatEligibilityRuleDTO.from_nft_collection_rule(rule)
                        for rule in eligibility_rules.nft_collections
                    ),
                    *(
                        TelegramChatEligibilityRuleDTO.from_whitelist_rule(rule)
                        for rule in eligibility_rules.whitelist_sources
                    ),
                    *(
                        TelegramChatEligibilityRuleDTO.from_whitelist_external_rule(
                            rule
                        )
                        for rule in eligibility_rules.whitelist_external_sources
                    ),
                ],
                key=lambda rule: (not rule.is_enabled, rule.category.value, rule.title),
            ),
        )
