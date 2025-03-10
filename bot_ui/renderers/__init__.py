import logging

from pytonapi.utils import raw_to_userfriendly
from pytonconnect import TonConnect
from sqlalchemy.orm import Session
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

from core.actions.authorization import AuthorizationAction
from core.dtos.chat import TelegramChatEligibilitySummaryDTO
from core.dtos.user import TelegramUserDTO
from core.models.user import User
from core.services.chat.user import TelegramChatUserService
from core.services.db import DBService
from core.services.user import UserService
from bot_ui.settings import bot_ui_settings

MAIN_BUTTON_REPLY_MARKUP = InlineKeyboardMarkup.from_button(
    InlineKeyboardButton(text="Main", callback_data="main")
)


logger = logging.getLogger(__name__)


async def connected_wallet_response(
    db_session: Session,
    user: User,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    edit_mode: bool = False,
) -> None:
    action = AuthorizationAction(db_session)
    eligibility_summary = action.is_user_eligible_chat_member(
        chat_id=bot_ui_settings.target_common_chat_id,
        user_id=user.id,
    )
    telegram_chat_user_service = TelegramChatUserService(db_session)
    is_chat_member = telegram_chat_user_service.is_chat_member(
        chat_id=bot_ui_settings.target_common_chat_id,
        user_id=user.id,
    )
    await connected_wallet_welcome_renderer(
        update,
        context,
        user=user,
        eligibility_summary=eligibility_summary,
        is_member=is_chat_member,
        edit_mode=edit_mode,
    )


async def connected_wallet_welcome_renderer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    eligibility_summary: TelegramChatEligibilitySummaryDTO,
    is_member: bool = False,
    edit_mode: bool = False,
) -> None:
    keyboard = [
        InlineKeyboardButton(text="Disconnect wallet", callback_data="disconnect")
    ]
    user_address = raw_to_userfriendly(user.wallet.address)
    shorten_address_escaped = escape_markdown(
        f"{user_address[:4]}..{user_address[-4:]}", version=2
    )
    text_lines = [
        f"Connected wallet: [{shorten_address_escaped}](https://tonscan.org/address/{user_address}) {'hidden' if user.wallet.hide_wallet else 'public'}\n",
    ]

    text_lines.extend(
        [
            escape_markdown(
                f"{rule.title}: {rule.current_human_friendly}/{rule.expected_human_friendly} {'✅' if rule.is_eligible else '❌'}",
                version=2,
            )
            for rule in eligibility_summary.items
        ]
    )
    text_lines.append(
        escape_markdown(
            f"Private chat member: {'✅' if is_member else '❌'}", version=2
        )
    )

    if not is_member and eligibility_summary:
        keyboard.append(
            InlineKeyboardButton(text="Join 8 club 🎱", callback_data="join-club")
        )

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
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    else:
        return await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="\n".join(text_lines),
            reply_markup=InlineKeyboardMarkup.from_column(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )


async def start_renderer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        if user.wallet:
            return await connected_wallet_response(
                db_session=db_session,
                user=user,
                context=context,
                update=update,
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
