import logging

from pytonapi.utils import userfriendly_to_raw
from telegram import Update
from telegram.ext import ContextTypes

from core.services.chat import ChatService
from core.services.db import DBService
from core.services.user import UserService
from core.services.wallet import WalletService
from core.settings import Config


logger = logging.Logger(__name__)


async def chat_join_request_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    invite_link_request = update.chat_join_request.invite_link
    with DBService().db_session() as db_session:
        user = UserService(db_session).get_or_create(
            telegram_user=update.effective_user
        )
        chat_service = ChatService(db_session)
        if not chat_service.validate_invite_link(
            user_id=user.id,
            invite_link=invite_link_request.invite_link,
        ):
            logger.warning(
                f"User `{user.telegram_id}` tried to join chat {update.effective_chat.id} with invalid invite link"
            )
            return await context.bot.decline_chat_join_request(
                chat_id=update.effective_chat.id,
                user_id=update.effective_user.id,
            )

        wallet_service = WalletService(db_session)
        is_nft_holder = wallet_service.is_nft_holder(
            owner_address=user.wallet.address,
            collection_address=userfriendly_to_raw(
                Config.TARGET_NFT_COLLECTION_ADDRESS
            ),
        )
        if not user.is_eligible_club_member(is_nft_holder=is_nft_holder):
            logger.warning(
                f"User `{user.telegram_id}` tried to join chat {update.effective_chat.id} without eligibility"
            )
            return await context.bot.decline_chat_join_request(
                chat_id=update.effective_chat.id,
                user_id=update.effective_user.id,
            )
        logger.info(
            f"User `{user.telegram_id}` joined chat {update.effective_chat.id} with invite link {invite_link_request.invite_link}"
        )
        await context.bot.approve_chat_join_request(
            chat_id=update.effective_chat.id,
            user_id=update.effective_user.id,
        )
        chat_service.mark_invite_link_activated(
            invite_link=invite_link_request.invite_link
        )
        await context.bot.revoke_chat_invite_link(
            chat_id=update.effective_chat.id,
            invite_link=invite_link_request.invite_link,
        )
