__all__ = ["handlers"]

from telegram.ext import CallbackQueryHandler

from core.handlers.callback.start import main_callback_handler
from core.handlers.callback.wallet import connect_wallet_handler, disconnect_wallet_handler

handlers = [
    CallbackQueryHandler(
        connect_wallet_handler,
        pattern=r"connect:\w",
    ),
    CallbackQueryHandler(
        disconnect_wallet_handler,
        pattern="disconnect",
    ),
    CallbackQueryHandler(
        main_callback_handler,
        pattern="main",
    ),
]
