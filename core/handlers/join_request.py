import logging

from telegram import Update
from telegram.ext import ContextTypes

from core.actions.authorization import AuthorizationAction
from core.dtos.user import TelegramUserDTO
from core.services.db import DBService
from core.services.user import UserService

logger = logging.Logger(__name__)


async def chat_join_request_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    with DBService().db_session() as db_session:
        user = UserService(db_session).get_or_create(
            telegram_user=TelegramUserDTO(
                id=update.effective_user.id,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name,
                username=update.effective_user.username,
                is_premium=update.effective_user.is_premium,
                language_code=update.effective_user.language_code,
            )
        )

        authorization_action = AuthorizationAction(db_session)
        eligibility_summary = authorization_action.is_user_eligible_chat_member(
            user_id=user.id,
            chat_id=update.effective_chat.id,
        )
        if not eligibility_summary:
            logger.warning(
                f"User {user.telegram_id!r} tried to join chat {update.effective_chat.id!r} but is not eligible"
            )
            return await context.bot.decline_chat_join_request(
                chat_id=update.effective_chat.id,
                user_id=update.effective_user.id,
            )
        logger.info(
            f"User {user.telegram_id!r} was approved to join the chat {update.effective_chat.id!r}."
        )
        await context.bot.approve_chat_join_request(
            chat_id=update.effective_chat.id,
            user_id=update.effective_user.id,
        )
