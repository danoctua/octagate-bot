import logging

from sqlalchemy.exc import NoResultFound
from telegram import Update
from telegram.ext import ContextTypes

from core.actions.authorization import AuthorizationAction
from core.dtos.user import TelegramUserDTO
from core.services.chat import TelegramChatUserService, TelegramChatService
from core.services.db import DBService
from core.services.user import UserService
from core.utils.chat import extract_member_status_change

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
                is_premium=update.effective_user.is_premium or False,
                language_code=update.effective_user.language_code,
            )
        )
        telegram_chat_service = TelegramChatService(db_session)
        try:
            telegram_chat_service.get(chat_id=update.effective_chat.id)
        except NoResultFound:
            logger.warning(
                f"Chat {update.effective_chat.id!r} not found in the database. Can't validate join request"
            )
            return

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
        telegram_user_chat_service = TelegramChatUserService(db_session)
        telegram_user_chat_service.create_or_update(
            chat_id=update.effective_chat.id,
            user_id=user.id,
            is_admin=False,
            is_whale_admin=False,
        )


async def chat_member_update_request_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    status_change = extract_member_status_change(update.chat_member)
    if not status_change:
        logger.info("No status change detected. Exit")
        return

    with DBService().db_session() as db_session:
        was_member, is_member = status_change
        telegram_chat_service = TelegramChatService(db_session)
        try:
            telegram_chat_service.get(chat_id=update.effective_chat.id)
        except NoResultFound:
            logger.warning(
                f"Chat {update.effective_chat.id!r} not found in the database. Can't update member status"
            )
            return

        if was_member and not is_member:
            user_service = UserService(db_session)
            try:
                user = user_service.get_by_telegram_id(
                    telegram_id=update.effective_user.id
                )
            except NoResultFound:
                logger.warning(
                    f"User {update.effective_user.id!r} not found in the database. Can't remove from the chat. Chat member {update.chat_member.from_user.id}"
                )
                return
            telegram_chat_user_service = TelegramChatUserService(db_session)
            telegram_chat_user_service.delete(
                chat_id=update.effective_chat.id, user_id=user.id
            )

            logger.info(
                f"User {update.effective_user.id!r} was removed from the chat {update.effective_chat.id!r}"
            )
        else:
            logger.info(
                f"User {update.effective_user.id!r} status was updated in the chat {update.effective_chat.id!r} but the state is not supported {was_member} -> {is_member}"
            )
