from datetime import datetime

from core.models.user import ChatUser
from core.services.base import BaseService


class ChatService(BaseService):
    def get_chat_user(self, user_id: int) -> ChatUser | None:
        return self.db_session.query(ChatUser).filter(ChatUser.user_id == user_id).one()

    def chat_user_exists(self, user_id: int) -> bool:
        return (
            self.db_session.query(ChatUser).filter(ChatUser.user_id == user_id).exists()
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
        return chat_user

    def mark_invite_link_activated(self, user_id: int) -> None:
        chat_user = self.get_chat_user(user_id)
        chat_user.invite_link_activated = True
        self.db_session.add(chat_user)
