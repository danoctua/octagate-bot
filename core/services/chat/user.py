from sqlalchemy import func
from sqlalchemy.exc import NoResultFound

from core.models import TelegramChatUser
from core.services.base import BaseService
from core.services.chat import logger


class TelegramChatUserService(BaseService):
    def create(self, chat_id: int, user_id: int, is_admin: bool) -> TelegramChatUser:
        chat_user = TelegramChatUser(
            chat_id=chat_id,
            user_id=user_id,
            is_admin=is_admin,
        )
        self.db_session.add(chat_user)
        self.db_session.commit()
        logger.debug(f"Telegram Chat User {chat_user!r} created.")
        return chat_user

    def get(self, chat_id: int, user_id: int) -> TelegramChatUser:
        return (
            self.db_session.query(TelegramChatUser)
            .filter(
                TelegramChatUser.chat_id == chat_id, TelegramChatUser.user_id == user_id
            )
            .one()
        )

    def get_members_count(self, chat_id: int) -> int:
        return (
            self.db_session.query(TelegramChatUser)
            .filter(TelegramChatUser.chat_id == chat_id)
            .count()
        )

    def get_members_count_by_chat_id(
        self, chat_ids: list[int] | None = None
    ) -> dict[int, int]:
        query = self.db_session.query(
            TelegramChatUser.chat_id, func.count(TelegramChatUser.user_id)
        )
        if chat_ids:
            query = query.filter(TelegramChatUser.chat_id.in_(chat_ids))

        query = query.group_by(TelegramChatUser.chat_id)
        return dict(query.all())

    def get_all(self, user_ids: list[int] | None = None) -> list[TelegramChatUser]:
        query = self.db_session.query(TelegramChatUser)

        if user_ids:
            query = query.filter(TelegramChatUser.user_id.in_(user_ids))

        return query.all()

    def find(self, chat_id: int, user_id: int) -> TelegramChatUser | None:
        try:
            return self.get(chat_id, user_id)
        except NoResultFound:
            return None

    def update(self, chat_user: TelegramChatUser, is_admin: bool) -> TelegramChatUser:
        chat_user.is_admin = is_admin
        self.db_session.commit()
        logger.debug(f"Telegram Chat User {chat_user!r} updated.")
        return chat_user

    def create_or_update(
        self, chat_id: int, user_id: int, is_admin: bool
    ) -> TelegramChatUser:
        try:
            chat_user = self.get(chat_id, user_id)
            return self.update(
                chat_user=chat_user,
                is_admin=is_admin,
            )
        except NoResultFound:
            logger.debug(
                f"No Telegram Chat User for chat_id {chat_id!r} and user_id {user_id!r} found. Creating new Telegram Chat User."
            )
            return self.create(
                chat_id,
                user_id,
                is_admin,
            )

    def is_chat_member(self, chat_id: int, user_id: int) -> bool:
        return (
            self.db_session.query(TelegramChatUser)
            .filter(
                TelegramChatUser.chat_id == chat_id, TelegramChatUser.user_id == user_id
            )
            .count()
            > 0
        )

    def promote_admin(self, chat_id: int, user_id: int) -> None:
        chat_user = self.get(chat_id, user_id)
        chat_user.is_admin = True
        self.db_session.commit()
        logger.debug(f"Telegram Chat User {chat_user!r} promoted to admin.")

    def demote_admin(self, chat_id: int, user_id: int) -> None:
        chat_user = self.get(chat_id, user_id)
        chat_user.is_admin = False
        self.db_session.commit()
        logger.debug(f"Telegram Chat User {chat_user!r} demoted from admin.")

    def delete(self, chat_id: int, user_id: int) -> None:
        self.db_session.query(TelegramChatUser).filter(
            TelegramChatUser.chat_id == chat_id,
            TelegramChatUser.user_id == user_id,
        ).delete(synchronize_session="fetch")
        self.db_session.commit()
        logger.debug(f"Telegram Chat User {user_id!r} in chat {chat_id!r} deleted.")
