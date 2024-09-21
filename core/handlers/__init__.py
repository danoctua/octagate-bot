from telegram.ext import ChatJoinRequestHandler

from core.handlers.join_request import chat_join_request_callback

handlers = [
    ChatJoinRequestHandler(
        chat_join_request_callback,
        # chat_id=Config.TARGET_COMMON_CHAT_ID,
    ),
]
