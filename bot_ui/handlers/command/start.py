import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot_ui.renderers import start_renderer

logger = logging.Logger(__name__)


async def start_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    return await start_renderer(update, context)
