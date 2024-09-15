from telegram import Update
from telegram.ext import ContextTypes

from core.renderers import start_renderer


async def main_callback_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await update.callback_query.answer()
    return await start_renderer(update, context)
