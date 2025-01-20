from telegram.ext import CommandHandler, filters

from bot_ui.handlers.command.start import start_handler

__all__ = ["handlers"]

handlers = [
    CommandHandler("start", start_handler, filters=filters.ChatType.PRIVATE),
]
