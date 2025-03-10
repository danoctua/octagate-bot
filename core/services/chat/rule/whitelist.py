import logging
from typing import TypeVar, Generic

from sqlalchemy import desc

from core.dtos.chat import TelegramChatWhitelistDTO
from core.models.chat import TelegramChatWhitelistExternalSource, TelegramChatWhitelist
from core.services.base import BaseService


logger = logging.getLogger(__name__)


TelegramChatWhitelistBaseT = TypeVar(
    "TelegramChatWhitelistBaseT",
    bound=TelegramChatWhitelistExternalSource | TelegramChatWhitelist,
)


class BaseTelegramChatExternalSourceService(
    BaseService, Generic[TelegramChatWhitelistBaseT]
):
    model: TelegramChatWhitelistBaseT

    def get(self, source_id: int) -> TelegramChatWhitelistBaseT:
        return (
            self.db_session.query(self.model).filter(self.model.id == source_id).one()
        )

    def get_all(
        self, chat_id: int | None = None, enabled_only: bool = True
    ) -> list[TelegramChatWhitelistBaseT]:
        query = self.db_session.query(self.model)
        if chat_id is not None:
            query = query.filter(self.model.chat_id == chat_id)
        if enabled_only:
            query = query.filter(self.model.is_enabled.is_(True))
        return query.order_by(
            desc(self.model.is_enabled), desc(self.model.created_at)
        ).all()

    def set_content(
        self, source_id: int, content: TelegramChatWhitelistDTO
    ) -> TelegramChatWhitelistBaseT:
        source = self.get(source_id)
        source.content = content.model_dump()
        self.db_session.commit()
        return source

    def delete(self, source_id: int) -> None:
        self.db_session.query(self.model).filter(self.model.id == source_id).delete(
            synchronize_session="fetch"
        )
        self.db_session.commit()
        logger.debug(f"Telegram Chat External Source {source_id!r} deleted.")


class TelegramChatExternalSourceService(
    BaseTelegramChatExternalSourceService[TelegramChatWhitelistExternalSource]
):
    model = TelegramChatWhitelistExternalSource

    def create(
        self, chat_id: int, description: str, external_source_url: str
    ) -> TelegramChatWhitelistExternalSource:
        new_source = self.model(
            chat_id=chat_id,
            url=external_source_url,
            description=description,
        )
        self.db_session.add(new_source)
        self.db_session.commit()
        return new_source

    def update(
        self,
        source_id: int,
        description: str,
        external_source_url: str,
        is_enabled: bool,
    ) -> TelegramChatWhitelistExternalSource:
        source = self.get(source_id)
        source.url = external_source_url
        source.description = description
        source.is_enabled = is_enabled
        self.db_session.commit()
        return source


class TelegramChatWhitelistService(
    BaseTelegramChatExternalSourceService[TelegramChatWhitelist]
):
    model = TelegramChatWhitelist

    def create(
        self, chat_id: int, name: str, description: str | None
    ) -> TelegramChatWhitelist:
        new_source = self.model(
            chat_id=chat_id,
            name=name,
            description=description,
        )
        self.db_session.add(new_source)
        self.db_session.commit()
        return new_source

    def update(
        self, source_id: int, name: str, description: str | None, is_enabled: bool
    ) -> TelegramChatWhitelist:
        source = self.get(source_id)
        source.name = name
        source.description = description
        source.is_enabled = is_enabled
        self.db_session.commit()
        return source
