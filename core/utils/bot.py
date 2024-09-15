import logging

from telegram import Update, InlineKeyboardMarkup
from telegram.error import BadRequest, TimedOut
from telegram.ext import ContextTypes

from core.constants import POOL_TIMEOUT
from core.settings import Config

logger = logging.getLogger(__name__)


async def remove_previous_callbacks(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    ...
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id,
        text=update.effective_message.text,
    )


async def edit_or_send_message(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    message_id: int,
    text: str,
    reply_markup: InlineKeyboardMarkup,
):
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup,
            pool_timeout=POOL_TIMEOUT,
            write_timeout=POOL_TIMEOUT,
        )

    except BadRequest:
        logger.warning(
            "Can't edit message %d for chat %d. Sending it instead.",
            message_id,
            chat_id,
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            pool_timeout=POOL_TIMEOUT,
            write_timeout=POOL_TIMEOUT,
        )

    except TimedOut:
        logger.error(
            "Can't send a message with a game data to the chat %d because of timeout. Trying once again",
            chat_id,
        )
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup,
            pool_timeout=POOL_TIMEOUT,
            write_timeout=POOL_TIMEOUT,
        )


async def answer_callback_query(update: Update) -> None:
    if Config.ENABLE_CALLBACK_REPLIES and update.callback_query:
        try:
            await update.callback_query.answer()
        except BaseException as exc:
            # We can just ignore this if we're timing out on this request
            logger.debug("Can't answer callback query %s", exc)
            pass
