import logging

from sqlalchemy.exc import NoResultFound
from telethon.tl.types import Channel

from core.models.chat import TelegramChat, TelegramChatUser
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
        )
        self.db_session.add(chat)
        self.db_session.commit()
        logger.info(f"Telegram Chat {chat.title!r} created.")
        return chat

    def update(
        self, entity: Channel, chat: TelegramChat, logo_path: str
    ) -> TelegramChat:
        chat.username = entity.username
        chat.title = entity.title
        chat.is_forum = entity.forum
        chat.logo_path = logo_path
        self.db_session.commit()
        logger.info(f"Telegram Chat {chat.title!r} updated.")
        return chat

    def create_or_update(
        self, chat_id: int, entity: Channel, logo_path: str
    ) -> TelegramChat:
        try:
            chat = self.get(chat_id=chat_id)
            return self.update(entity, chat, logo_path=logo_path)
        except NoResultFound:
            logger.info(
                f"No Telegram Chat for ID {entity.id!r} found. Creating new Telegram Chat."
            )
            return self.create(chat_id=chat_id, entity=entity, logo_path=logo_path)

    def get(self, chat_id: int) -> TelegramChat:
        return (
            self.db_session.query(TelegramChat).filter(TelegramChat.id == chat_id).one()
        )

    def refresh_invite_link(self, chat_id: int, invite_link: str) -> TelegramChat:
        chat = self.get(chat_id)
        chat.invite_link = invite_link
        self.db_session.commit()
        logger.info(f"Telegram Chat {chat.title!r} invite link updated.")
        return chat


class TelegramChatUserService(BaseService):
    def create(
        self, chat_id: int, user_id: int, is_admin: bool, is_whale_admin: bool
    ) -> TelegramChatUser:
        chat_user = TelegramChatUser(
            chat_id=chat_id,
            user_id=user_id,
            is_admin=is_admin,
            is_whale_admin=is_whale_admin,
        )
        self.db_session.add(chat_user)
        self.db_session.commit()
        logger.info(f"Telegram Chat User {chat_user!r} created.")
        return chat_user

    def get(self, chat_id: int, user_id: int) -> TelegramChatUser:
        return (
            self.db_session.query(TelegramChatUser)
            .filter(
                TelegramChatUser.chat_id == chat_id, TelegramChatUser.user_id == user_id
            )
            .one()
        )

    def update(
        self, chat_user: TelegramChatUser, is_admin: bool, is_whale_admin: bool
    ) -> TelegramChatUser:
        chat_user.is_admin = is_admin
        chat_user.is_whale_admin = is_whale_admin
        self.db_session.commit()
        logger.info(f"Telegram Chat User {chat_user!r} updated.")
        return chat_user

    def create_or_update(
        self, chat_id: int, user_id: int, is_admin: bool, is_whale_admin: bool
    ) -> TelegramChatUser:
        try:
            chat_user = self.get(chat_id, user_id)
            return self.update(
                chat_user=chat_user, is_admin=is_admin, is_whale_admin=is_whale_admin
            )
        except NoResultFound:
            logger.info(
                f"No Telegram Chat User for chat_id {chat_id!r} and user_id {user_id!r} found. Creating new Telegram Chat User."
            )
            return self.create(chat_id, user_id, is_admin, is_whale_admin)
