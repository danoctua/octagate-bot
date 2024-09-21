import logging

from pytonapi.utils import userfriendly_to_raw
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatInviteLink
from telegram.ext import ContextTypes

from core.constants import DEFAULT_EXPIRY_TIMEOUT_MINUTES
from core.renderers import MAIN_BUTTON_REPLY_MARKUP
from core.services.chat import ChatService
from core.services.db import DBService
from core.services.user import UserService
from core.services.wallet import WalletService
from core.settings import Config
from core.utils.authorization import get_telegram_chat_member
from core.utils.bot import answer_callback_query, delete_message
from core.utils.date import generate_expire_date


logger = logging.getLogger(__name__)


async def join_club_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await answer_callback_query(update)
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        user = user_service.get_or_create(telegram_user=update.effective_user)
        if await get_telegram_chat_member(context, user.telegram_id) is not None:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You are already in the club!",
                reply_markup=MAIN_BUTTON_REPLY_MARKUP,
            )
            await delete_message(
                context, update.effective_chat.id, update.effective_message.message_id
            )
            return

        wallet_service = WalletService(db_session)
        is_nft_holder = wallet_service.is_nft_holder(
            owner_address=user.wallet.address,
            collection_address=userfriendly_to_raw(
                Config.TARGET_NFT_COLLECTION_ADDRESS
            ),
        )
        if not user.is_eligible_club_member(is_nft_holder=is_nft_holder):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You are not eligible to join the club!",
                reply_markup=MAIN_BUTTON_REPLY_MARKUP,
            )
            await delete_message(
                context, update.effective_chat.id, update.effective_message.message_id
            )
            return

        invite_link = None
        if user.chat_user:
            if not user.chat_user.is_invite_link_expired:
                invite_link = user.chat_user.invite_link

        if not invite_link:
            logger.info(
                "Creating a new invite link for user `%d` to join the club chat",
                user.telegram_id,
            )
            expiry = generate_expire_date(expire_in=DEFAULT_EXPIRY_TIMEOUT_MINUTES)
            invite_link_response: ChatInviteLink = (
                await context.bot.create_chat_invite_link(
                    chat_id=Config.TARGET_COMMON_CHAT_ID,
                    expire_date=expiry.replace(tzinfo=None),
                    name=f"Invite #{user.telegram_id}",
                    creates_join_request=True,
                )
            )
            invite_link = invite_link_response.invite_link
            chat_service = ChatService(db_session)
            chat_service.create_or_update_chat_user(
                user_id=user.id,
                invite_link=invite_link,
                invite_link_expiry=expiry,
            )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"Use the button below to join the chat.\n\n"
                f"That's your personal invite that will be valid for {DEFAULT_EXPIRY_TIMEOUT_MINUTES} minutes."
            ),
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(text="Join chat", url=invite_link)
            ),
        )
        await delete_message(
            context, update.effective_chat.id, update.effective_message.message_id
        )
