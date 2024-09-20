import logging

from pytonconnect import TonConnect
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from core.models.user import User
from core.services.db import DBService
from core.services.user import UserService


MAIN_BUTTON_REPLY_MARKUP = InlineKeyboardMarkup.from_button(
    InlineKeyboardButton(text="Main", callback_data="main")
)


logger = logging.getLogger(__name__)


async def connected_wallet_welcome_renderer(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user: User
) -> None:
    is_holder = user.wallet.jetton_wallet is not None
    reply_markup = InlineKeyboardMarkup.from_column(
        [InlineKeyboardButton(text="Disconnect wallet", callback_data="disconnect")]
    )
    text_lines = []
    if is_holder:
        text_lines.append("You are $ANON holder!")

        if user.wallet.jetton_wallet.is_whale:
            text_lines.append(f"🐋 You are whale #{user.wallet.jetton_wallet.rating}!")
        return await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="\n\n".join(text_lines),
            reply_markup=reply_markup,
        )
    else:
        return await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You are not a jetton holder!",
            reply_markup=reply_markup,
        )


async def start_renderer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        user = user_service.get_or_create(telegram_user=update.effective_user)
        if user.wallet:
            return await connected_wallet_welcome_renderer(update, context, user)
        else:
            wallets_list = TonConnect.get_wallets()
            reply_markup = InlineKeyboardMarkup.from_column(
                [
                    InlineKeyboardButton(
                        text=wallet["name"], callback_data=f'connect:{wallet["name"]}'
                    )
                    for wallet in wallets_list
                ]
            )
            return await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please select your wallet to connect:",
                reply_markup=reply_markup,
            )
