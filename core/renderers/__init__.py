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

MAIN_BUTTON_REPLY_MARKUP = InlineKeyboardMarkup.from_button(
    InlineKeyboardButton(text="Main", callback_data="main")
)


logger = logging.getLogger(__name__)


async def connected_wallet_welcome_renderer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    is_nft_holder: bool = False,
) -> None:
    reply_markup = InlineKeyboardMarkup.from_column(
        [InlineKeyboardButton(text="Disconnect wallet", callback_data="disconnect")]
    )
    text_lines = [
        f"Connected wallet: {raw_to_userfriendly(user.wallet.address)}\n",
    ]
    if is_nft_holder:
        text_lines.append("🥷 You are Anonymous Number holder!")
    else:
        text_lines.append("🤖 You are not Anonymous Number holder yet!")

    is_anon_holder = user.wallet.jetton_wallet is not None
    if is_anon_holder:
        text_lines.append(
            f"🎱 You are $ANON holder #{user.wallet.jetton_wallet.rating}!"
        )

        if user.wallet.jetton_wallet.is_whale:
            text_lines.append("🐋 You are $ANON whale!")

    else:
        text_lines.append("🎱 You are not $ANON holder yet!")

    return await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="\n".join(text_lines),
        reply_markup=reply_markup,
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
            logger.info(
                "{is_nft_holder}, {user.wallet.address}, {Config.TARGET_NFT_COLLECTION_ADDRESS}"
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
