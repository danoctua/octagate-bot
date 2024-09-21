from telegram import Update
from telegram.ext import ContextTypes

from core.renderers import start_renderer
from core.utils.bot import answer_callback_query, delete_message


async def main_callback_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await answer_callback_query(update)
    await start_renderer(update, context)
    await delete_message(
        context, update.effective_chat.id, update.effective_message.message_id
    )
