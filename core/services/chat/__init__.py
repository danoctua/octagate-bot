import logging

from slugify import slugify
from sqlalchemy.exc import NoResultFound
from telethon.tl.types import Channel

from core.models.chat import (
    TelegramChat,
)
from core.services.base import BaseService

logger = logging.getLogger(__name__)


class TelegramChatService(BaseService):
    def create(self, chat_id: int, entity: Channel, logo_path: str) -> TelegramChat:
        chat = TelegramChat(
            id=chat_id,
            username=entity.username,
            title=entity.title,
            is_forum=entity.forum,
            logo_path=logo_path,
            # TODO: handle cases with the same slug
            slug=slugify(entity.title),
        )
        self.db_session.add(chat)
        self.db_session.commit()
        logger.debug(f"Telegram Chat {chat.title!r} created.")
        return chat

    def update(
        self, entity: Channel, chat: TelegramChat, logo_path: str
    ) -> TelegramChat:
        chat.username = entity.username
        chat.title = entity.title
        chat.slug = slugify(entity.title)
        chat.is_forum = entity.forum
        chat.logo_path = logo_path
        self.db_session.commit()
        logger.debug(f"Telegram Chat {chat.title!r} updated.")
        return chat

    def update_description(self, chat: TelegramChat, description: str) -> TelegramChat:
        chat.description = description
        self.db_session.commit()
        logger.debug(f"Telegram Chat {chat.title!r} description updated.")
        return chat

    def create_or_update(
        self, chat_id: int, entity: Channel, logo_path: str
    ) -> TelegramChat:
        try:
            chat = self.get(chat_id=chat_id)
            return self.update(entity, chat, logo_path=logo_path)
        except NoResultFound:
            logger.debug(
                f"No Telegram Chat for ID {entity.id!r} found. Creating new Telegram Chat."
            )
            return self.create(chat_id=chat_id, entity=entity, logo_path=logo_path)

    def get(self, chat_id: int) -> TelegramChat:
        return (
            self.db_session.query(TelegramChat).filter(TelegramChat.id == chat_id).one()
        )

    def get_all(self, chat_ids: list[int] | None = None) -> list[TelegramChat]:
        query = self.db_session.query(TelegramChat)
        if chat_ids:
            query = query.filter(TelegramChat.id.in_(chat_ids))

        query = query.order_by(TelegramChat.id)
        return query.all()

    def refresh_invite_link(self, chat_id: int, invite_link: str) -> TelegramChat:
        chat = self.get(chat_id)
        chat.invite_link = invite_link
        self.db_session.commit()
        logger.debug(f"Telegram Chat {chat.title!r} invite link updated.")
        return chat

    def get_by_slug(self, slug: str) -> TelegramChat:
        return (
            self.db_session.query(TelegramChat).filter(TelegramChat.slug == slug).one()
        )

    def delete(self, chat_id: int) -> None:
        chat = self.get(chat_id)
        self.db_session.delete(chat)
        self.db_session.commit()
        logger.debug(f"Telegram Chat {chat.title!r} deleted.")

    def check_exists(self, chat_id: int) -> bool:
        return (
            self.db_session.query(TelegramChat)
            .filter(TelegramChat.id == chat_id)
            .count()
            > 0
        )
