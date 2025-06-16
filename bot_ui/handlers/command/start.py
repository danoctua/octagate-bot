import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from core.constants import (
    MIGRATION_TO_ACCESS_TEXT,
    MIGRATION_TO_ACCESS_BUTTON_TEXT,
    MIRATION_TO_ACCESS_BUTTON_URL,
)

logger = logging.Logger(__name__)


async def start_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await context.bot.send_message(
        text=MIGRATION_TO_ACCESS_TEXT,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(
                text=MIGRATION_TO_ACCESS_BUTTON_TEXT, url=MIRATION_TO_ACCESS_BUTTON_URL
            )
        ),
        parse_mode=ParseMode.MARKDOWN_V2,
        chat_id=update.effective_chat.id,
    )
