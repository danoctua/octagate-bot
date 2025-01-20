from telegram.ext import ChatJoinRequestHandler, ChatMemberHandler

from core.handlers.chat import (
    chat_join_request_callback,
    chat_member_update_request_callback,
)

handlers = [
    ChatJoinRequestHandler(
        chat_join_request_callback,
    ),
    ChatMemberHandler(
        chat_member_update_request_callback, ChatMemberHandler.ANY_CHAT_MEMBER
    ),
]
