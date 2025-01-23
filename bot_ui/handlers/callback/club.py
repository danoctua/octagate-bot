import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.dtos.user import TelegramUserDTO
from bot_ui.renderers import MAIN_BUTTON_REPLY_MARKUP
from core.services.chat import TelegramChatService, TelegramChatUserService
from core.services.db import DBService
from core.services.nft import NftItemService
from core.services.user import UserService
from core.services.wallet import JettonWalletService
from bot_ui.settings import bot_ui_settings
from bot_ui.utils import answer_callback_query, delete_message

logger = logging.getLogger(__name__)


# TODO: GH-3 deprecate
async def join_club_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await answer_callback_query(update)
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        user = user_service.get_or_create(
            telegram_user=TelegramUserDTO(
                id=update.effective_user.id,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name,
                username=update.effective_user.username,
                is_premium=update.effective_user.is_premium or False,
                language_code=update.effective_user.language_code,
            )
        )
        telegram_chat_user_service = TelegramChatUserService(db_session)
        if telegram_chat_user := telegram_chat_user_service.get(
            chat_id=bot_ui_settings.target_common_chat_id, user_id=user.id
        ):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You are already in the chat!",
                reply_markup=MAIN_BUTTON_REPLY_MARKUP,
            )
            await delete_message(
                context, update.effective_chat.id, update.effective_message.message_id
            )
            return

        eligibility_rules = telegram_chat_user_service.get_eligibility_rules(
            chat_id=bot_ui_settings.target_common_chat_id
        )
        nft_item_service = NftItemService(db_session)
        user_nft_items = nft_item_service.get_all(owner_address=user.wallet.address)
        jetton_wallet_service = JettonWalletService(db_session)
        user_jettons = jetton_wallet_service.get_all(owner_address=user.wallet.address)

        if not (
            telegram_chat_user_service.is_user_eligible_chat_member(
                eligibility_rules=eligibility_rules,
                user_jettons=user_jettons,
                user_nft_items=user_nft_items,
                chat_member=telegram_chat_user,
            )
        ):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You are not eligible to join the club!",
                reply_markup=MAIN_BUTTON_REPLY_MARKUP,
            )
            await delete_message(
                context, update.effective_chat.id, update.effective_message.message_id
            )
            return

        telegram_chat_service = TelegramChatService(db_session)
        telegram_chat = telegram_chat_service.get(bot_ui_settings.target_common_chat_id)

        if not telegram_chat.invite_link:
            return await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="The chat is not ready yet. Please try again later.",
                reply_markup=MAIN_BUTTON_REPLY_MARKUP,
            )

        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=("Use the button below to join the chat.\n\n"),
                reply_markup=InlineKeyboardMarkup.from_button(
                    InlineKeyboardButton(
                        text="Join chat", url=telegram_chat.invite_link
                    )
                ),
            )
        await delete_message(
            context, update.effective_chat.id, update.effective_message.message_id
        )
