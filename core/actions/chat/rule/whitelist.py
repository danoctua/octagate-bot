import logging

from httpx import HTTPError
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from core.actions.authorization import AuthorizationAction
from core.actions.base import BaseAction
from core.dtos.chat import (
    TelegramChatWhitelistDifferenceDTO,
    TelegramChatWhitelistExternalSourceDTO,
    TelegramChatWhitelistDTO,
)
from core.models.chat import TelegramChatWhitelistExternalSource
from core.services.chat import TelegramChatService
from core.services.chat.rule.whitelist import (
    TelegramChatExternalSourceService,
    TelegramChatWhitelistService,
)
from core.services.chat.user import TelegramChatUserService
from core.utils.external_source import fetch_whitelist_members
from core.exceptions.chat import (
    TelegramChatInvalidExternalSourceError,
    TelegramChatNotExists,
)

logger = logging.getLogger(__name__)


class TelegramChatWhitelistExternalSourceAction(BaseAction):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.telegram_chat_service = TelegramChatService(db_session)
        self.telegram_chat_user_service = TelegramChatUserService(db_session)
        self.telegram_chat_external_source_service = TelegramChatExternalSourceService(
            db_session
        )

    def get(self, rule_id: int) -> TelegramChatWhitelistExternalSourceDTO:
        external_source = self.telegram_chat_external_source_service.get(rule_id)
        return TelegramChatWhitelistExternalSourceDTO.from_orm(external_source)

    async def create(
        self, slug: str, external_source_url: str, name: str, description: str | None
    ) -> TelegramChatWhitelistExternalSourceDTO:
        try:
            chat = self.telegram_chat_service.get_by_slug(slug)
        except NoResultFound:
            raise TelegramChatNotExists(f"Chat {slug!r} not found")
        external_source = self.telegram_chat_external_source_service.create(
            chat_id=chat.id,
            external_source_url=external_source_url,
            name=name,
            description=description,
        )
        try:
            await self._refresh_external_source(
                source=external_source, raise_for_error=True
            )
        except Exception as e:
            logger.warning(
                "Rolling back transaction as an error occurred while validating the source"
            )
            self.db_session.rollback()
            raise e
        # No need for a manual commit, as it's already done in the service during set_content
        return TelegramChatWhitelistExternalSourceDTO.from_orm(external_source)

    async def update(
        self,
        rule_id: int,
        external_source_url: str,
        name: str,
        description: str | None,
        is_enabled: bool,
    ) -> TelegramChatWhitelistExternalSourceDTO:
        external_source = self.telegram_chat_external_source_service.update(
            rule_id=rule_id,
            external_source_url=external_source_url,
            name=name,
            description=description,
            is_enabled=is_enabled,
        )
        try:
            await self._refresh_external_source(
                source=external_source, raise_for_error=True
            )
        except Exception as e:
            logger.warning(
                "Rolling back transaction as an error occurred while validating the source"
            )
            self.db_session.rollback()
            raise e
        # No need for a manual commit, as it's already done in the service during set_content
        return TelegramChatWhitelistExternalSourceDTO.from_orm(external_source)

    def _set_content(
        self, rule: TelegramChatWhitelistExternalSource, content: list[int]
    ) -> TelegramChatWhitelistExternalSourceDTO:
        external_source = self.telegram_chat_external_source_service.set_content(
            rule=rule, content=content
        )
        return TelegramChatWhitelistExternalSourceDTO.from_orm(external_source)

    async def _refresh_external_source(
        self,
        source: TelegramChatWhitelistExternalSource,
        raise_for_error: bool = False,
    ) -> None:
        try:
            result = await fetch_whitelist_members(source.url)
        except HTTPError as e:
            logger.warning(f"Failed to fetch external source {source.url!r}: {e}")
            if raise_for_error:
                raise
            return
        except TelegramChatInvalidExternalSourceError as e:
            logger.error(f"Invalid external source {source.url!r}: {e}")
            if raise_for_error:
                raise
            return
        except Exception as e:
            logger.error(f"Failed to fetch external source {source.url!r}: {e}")
            if raise_for_error:
                raise
            return

        difference = TelegramChatWhitelistDifferenceDTO(
            previous=source.content,
            current=result.users,
        )

        self._set_content(rule=source, content=result.users)

        chat_members = self.telegram_chat_user_service.get_all(
            user_ids=difference.removed
        )
        authorization_action = AuthorizationAction(self.db_session)
        await authorization_action.kick_ineligible_chat_members(
            chat_members=chat_members
        )

        logger.info(f"Refreshed external source {source.url!r} successfully")

    async def refresh_enabled(self, raise_for_error: bool = False) -> None:
        sources = self.telegram_chat_external_source_service.get_all(enabled_only=True)
        for source in sources:
            await self._refresh_external_source(source, raise_for_error=raise_for_error)

    def delete(self, rule_id: int) -> None:
        self.telegram_chat_external_source_service.delete(rule_id=rule_id)


class TelegramChatWhitelistAction(BaseAction):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.telegram_chat_service = TelegramChatService(db_session)
        self.telegram_chat_user_service = TelegramChatUserService(db_session)
        self.telegram_chat_whitelist_service = TelegramChatWhitelistService(db_session)

    def get(self, rule_id: int) -> TelegramChatWhitelistDTO:
        whitelist = self.telegram_chat_whitelist_service.get(rule_id)
        return TelegramChatWhitelistDTO.from_orm(whitelist)

    def create(
        self, slug: str, name: str, description: str | None = None
    ) -> TelegramChatWhitelistDTO:
        try:
            chat = self.telegram_chat_service.get_by_slug(slug)
        except NoResultFound:
            raise TelegramChatNotExists(f"Chat {slug!r} not found")
        whitelist = self.telegram_chat_whitelist_service.create(
            chat_id=chat.id,
            name=name,
            description=description,
        )
        return TelegramChatWhitelistDTO.from_orm(whitelist)

    def update(
        self, rule_id: int, name: str, description: str | None, is_enabled: bool
    ) -> TelegramChatWhitelistDTO:
        whitelist = self.telegram_chat_whitelist_service.update(
            rule_id=rule_id,
            name=name,
            description=description,
            is_enabled=is_enabled,
        )
        return TelegramChatWhitelistDTO.from_orm(whitelist)

    async def set_content(
        self, rule_id: int, content: list[int]
    ) -> TelegramChatWhitelistDTO:
        rule = self.telegram_chat_whitelist_service.get(rule_id)
        whitelist = self.telegram_chat_whitelist_service.set_content(
            rule=rule, content=content
        )
        difference = TelegramChatWhitelistDifferenceDTO(
            previous=rule.content,
            current=content,
        )

        if difference.removed:
            chat_members = self.telegram_chat_user_service.get_all(
                user_ids=difference.removed
            )
            authorization_action = AuthorizationAction(self.db_session)
            await authorization_action.kick_ineligible_chat_members(
                chat_members=chat_members
            )

        logger.info(f"Whitelist {rule_id!r} updated successfully")
        return TelegramChatWhitelistDTO.from_orm(whitelist)

    def delete(self, rule_id: int) -> None:
        self.telegram_chat_whitelist_service.delete(rule_id=rule_id)
