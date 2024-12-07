import logging

from pytonapi.utils import raw_to_userfriendly, userfriendly_to_raw
from pytonconnect import TonConnect
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from core.models.user import User
from core.services.db import DBService
from core.services.user import UserService
from core.services.wallet import WalletService
from core.settings import Config
from core.utils.authorization import get_telegram_chat_member

MAIN_BUTTON_REPLY_MARKUP = InlineKeyboardMarkup.from_button(
    InlineKeyboardButton(text="Main", callback_data="main")
)


logger = logging.getLogger(__name__)


async def connected_wallet_welcome_renderer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    is_nft_holder: bool = False,
    edit_mode: bool = False,
) -> None:
    keyboard = [
        InlineKeyboardButton(text="Disconnect wallet", callback_data="disconnect")
    ]
    text_lines = [
        f"Connected wallet: {raw_to_userfriendly(user.wallet.address)}\n",
    ]
    if is_nft_holder:
        text_lines.append("🥷 You are Anonymous Number holder!")
    else:
        text_lines.append("🤖 You are not Anonymous Number holder yet!")

    is_anon_holder = (
        user.wallet.jetton_wallet is not None and user.wallet.jetton_wallet.balance > 0
    )
    if is_anon_holder:
        text_lines.append(
            f"🎱 You are $ANON holder #{user.wallet.jetton_wallet.rating}!"
        )

        if user.wallet.jetton_wallet.is_whale:
            text_lines.append("🐋 You are $ANON whale!")

        if user.wallet.hide_wallet:
            text_lines.append("🔒 Wallet is hidden")

    else:
        text_lines.append("🎱 You are not $ANON holder yet!")

    chat_member = await get_telegram_chat_member(context, user.telegram_id)

    if chat_member is None and user.is_eligible_club_member(
        is_nft_holder=is_nft_holder
    ):
        keyboard.append(
            InlineKeyboardButton(text="Join 8 club 🎱", callback_data="join-club")
        )

    if user.wallet:
        keyboard.insert(
            0,
            InlineKeyboardButton(
                text="Hide wallet" if not user.wallet.hide_wallet else "Show wallet",
                callback_data="hide-wallet"
                if not user.wallet.hide_wallet
                else "show-wallet",
            ),
        )

    if edit_mode:
        return await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id,
            text="\n".join(text_lines),
            reply_markup=InlineKeyboardMarkup.from_column(keyboard),
        )
    else:
        return await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="\n".join(text_lines),
            reply_markup=InlineKeyboardMarkup.from_column(keyboard),
        )


async def start_renderer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        user = user_service.get_or_create(telegram_user=update.effective_user)
        if user.wallet:
            wallet_service = WalletService(db_session)
            is_nft_holder = wallet_service.is_nft_holder(
                owner_address=user.wallet.address,
                collection_address=userfriendly_to_raw(
                    Config.TARGET_NFT_COLLECTION_ADDRESS
                ),
            )
            return await connected_wallet_welcome_renderer(
                update, context, user, is_nft_holder
            )
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
