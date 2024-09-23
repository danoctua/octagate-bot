import logging
from datetime import datetime

from sqlalchemy.exc import NoResultFound

from core.models.user import ChatUser
from core.services.base import BaseService


logger = logging.getLogger(__name__)


class ChatService(BaseService):
    def get_chat_user(self, user_id: int) -> ChatUser | None:
        return self.db_session.query(ChatUser).filter(ChatUser.user_id == user_id).one()

    def chat_user_exists(self, user_id: int) -> bool:
        return (
            self.db_session.query(ChatUser).filter(ChatUser.user_id == user_id).count()
            > 0
        )

    def create_chat_user(
        self, user_id: int, invite_link: str, invite_link_expiry: datetime
    ) -> ChatUser:
        chat_user = ChatUser(
            user_id=user_id,
            invite_link=invite_link,
            invite_link_expiry=invite_link_expiry,
        )
        self.db_session.add(chat_user)
        self.db_session.commit()
        return chat_user

    def update_chat_user(
        self, user_id: int, invite_link: str, invite_link_expiry: datetime
    ) -> None:
        self.db_session.query(ChatUser).filter(ChatUser.user_id == user_id).update(
            {
                "invite_link": invite_link,
                "invite_link_expiry": invite_link_expiry,
            }
        )
        self.db_session.commit()

    def create_or_update_chat_user(
        self, user_id: int, invite_link: str, invite_link_expiry: datetime
    ) -> None:
        if self.chat_user_exists(user_id):
            self.update_chat_user(user_id, invite_link, invite_link_expiry)
        else:
            self.create_chat_user(user_id, invite_link, invite_link_expiry)

    def mark_invite_link_activated(self, invite_link: str) -> None:
        self.db_session.query(ChatUser).filter(
            ChatUser.invite_link == invite_link
        ).update({"invite_link_activated": True})
        self.db_session.commit()

    def validate_invite_link(self, user_id: int, invite_link: str) -> bool:
        try:
            chat_user = self.get_chat_user(user_id)
        except NoResultFound:
            logger.warning(f"Chat user not found for user_id: {user_id}")
            return False

        return (
            chat_user.invite_link == invite_link
            and not chat_user.invite_link_activated
            and not chat_user.is_invite_link_expired
        )
