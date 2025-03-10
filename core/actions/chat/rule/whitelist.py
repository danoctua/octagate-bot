import logging

from httpx import HTTPError
from sqlalchemy.orm import Session

from core.actions.authorization import AuthorizationAction
from core.actions.base import BaseAction
from core.dtos.chat import (
    TelegramChatWhitelistDTO,
    TelegramChatWhitelistDifferenceDTO,
    TelegramChatExternalSourceDTO,
)
from core.services.chat import TelegramChatService
from core.services.chat.rule.whitelist import (
    TelegramChatExternalSourceService,
    TelegramChatWhitelistService,
)
from core.services.chat.user import TelegramChatUserService
from core.utils.external_source import fetch_whitelist_members
from core.exceptions.chat import TelegramChatInvalidExternalSourceError

logger = logging.getLogger(__name__)


class TelegramChatWhitelistExternalSourceAction(BaseAction):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.telegram_chat_service = TelegramChatService(db_session)
        self.telegram_chat_user_service = TelegramChatUserService(db_session)
        self.telegram_chat_external_source_service = TelegramChatExternalSourceService(
            db_session
        )

    def create(
        self, chat_id: int, external_source_url: str, description: str
    ) -> TelegramChatExternalSourceDTO:
        external_source = self.telegram_chat_external_source_service.create(
            chat_id=chat_id,
            external_source_url=external_source_url,
            description=description,
        )
        return TelegramChatExternalSourceDTO.from_orm(external_source)

    def update(
        self,
        source_id: int,
        external_source_url: str,
        description: str,
        is_enabled: bool,
    ) -> TelegramChatExternalSourceDTO:
        external_source = self.telegram_chat_external_source_service.update(
            source_id=source_id,
            external_source_url=external_source_url,
            description=description,
            is_enabled=is_enabled,
        )
        return TelegramChatExternalSourceDTO.from_orm(external_source)

    def set_content(
        self, source_id: int, content: TelegramChatWhitelistDTO
    ) -> TelegramChatExternalSourceDTO:
        external_source = self.telegram_chat_external_source_service.set_content(
            source_id=source_id, content=content
        )
        return TelegramChatExternalSourceDTO.from_orm(external_source)

    async def refresh_enabled(self) -> None:
        sources = self.telegram_chat_external_source_service.get_all(enabled_only=True)
        for source in sources:
            try:
                result = await fetch_whitelist_members(source.url)
            except HTTPError as e:
                logger.warning(f"Failed to fetch external source {source.url!r}: {e}")
                continue
            except TelegramChatInvalidExternalSourceError as e:
                logger.error(f"Invalid external source {source.url!r}: {e}")
                continue
            except Exception as e:
                logger.error(f"Failed to fetch external source {source.url!r}: {e}")
                continue

            difference = TelegramChatWhitelistDifferenceDTO(
                previous=TelegramChatWhitelistDTO.model_validate(source.content),
                current=result,
            )

            self.set_content(source_id=source.id, content=result)

            chat_members = self.telegram_chat_user_service.get_all(
                user_ids=difference.removed
            )
            authorization_action = AuthorizationAction(self.db_session)
            await authorization_action.kick_ineligible_chat_members(
                chat_members=chat_members
            )

            logger.info(f"Refreshed external source {source.url!r} successfully")

    def delete(self, source_id: int) -> None:
        self.telegram_chat_external_source_service.delete(source_id=source_id)


class TelegramChatWhitelistAction(BaseAction):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.telegram_chat_service = TelegramChatService(db_session)
        self.telegram_chat_user_service = TelegramChatUserService(db_session)
        self.telegram_chat_whitelist_service = TelegramChatWhitelistService(db_session)

    def create(
        self, chat_id: int, name: str, description: str | None = None
    ) -> TelegramChatWhitelistDTO:
        whitelist = self.telegram_chat_whitelist_service.create(
            chat_id=chat_id,
            name=name,
            description=description,
        )
        return TelegramChatWhitelistDTO.model_validate(whitelist.content)

    def update(
        self, source_id: int, name: str, description: str | None, is_enabled: bool
    ) -> TelegramChatWhitelistDTO:
        whitelist = self.telegram_chat_whitelist_service.update(
            source_id=source_id,
            name=name,
            description=description,
            is_enabled=is_enabled,
        )
        return TelegramChatWhitelistDTO.model_validate(whitelist.content)

    def set_content(
        self, source_id: int, content: TelegramChatWhitelistDTO
    ) -> TelegramChatWhitelistDTO:
        whitelist = self.telegram_chat_whitelist_service.set_content(
            source_id=source_id, content=content
        )
        return TelegramChatWhitelistDTO.model_validate(whitelist.content)

    def delete(self, source_id: int) -> None:
        self.telegram_chat_whitelist_service.delete(source_id=source_id)
