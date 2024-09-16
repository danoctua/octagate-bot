import logging

from pytonconnect import TonConnect
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from core.models.user import User
from core.services.db import DBService
from core.services.user import UserService
from core.settings import Config


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
    if is_holder:
        text = "You are $ANON holder!"

        if user.wallet.jetton_wallet.is_whale:
            # chat_admins = await context.bot.get_chat_administrators(
            #     chat_id=Config.TARGET_COMMON_CHAT_ID
            # )
            # chat_admins_ids = [admin.user.id for admin in chat_admins]
            if update.effective_user.id:
                logger.info(
                    "Promoting user `%d` to admin in the chat", update.effective_user.id
                )
                await context.bot.promote_chat_member(
                    chat_id=Config.TARGET_COMMON_CHAT_ID,
                    user_id=update.effective_user.id,
                    can_post_messages=True,
                    can_manage_chat=True,
                    can_manage_topics=True,
                )
                await context.bot.set_chat_administrator_custom_title(
                    chat_id=Config.TARGET_COMMON_CHAT_ID,
                    user_id=update.effective_user.id,
                    custom_title=f"8x{user.wallet.jetton_wallet.rating}",
                )
            else:
                logger.info(
                    "User `%d` is already an admin in the chat",
                    update.effective_user.id,
                )
            text += (
                f"\n\nYou've been promoted to admins in the chat "
                f"as you're whale #{user.wallet.jetton_wallet.rating}!"
            )
        return await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
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
