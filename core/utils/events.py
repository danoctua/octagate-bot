from typing import Any, Optional

from telethon.events.common import EventBuilder, EventCommon
from telethon.tl import TLObject
from telethon.tl.types import UpdateBotChatInviteRequester


class ChatJoinRequestEvent(EventBuilder):
    @classmethod
    def build(
        cls, update: TLObject, others: Any = None, self_id: int | None = None
    ) -> Optional["Event"]:
        if isinstance(update, UpdateBotChatInviteRequester):
            return cls.Event(update=update)

    class Event(EventCommon):
        def __init__(self, *, update: UpdateBotChatInviteRequester):
            super().__init__(chat_peer=update.peer)
            self.original_update = update
            self.user_id = update.user_id

        @property
        def user(self):
            return self._entities.get(self.user_id)
