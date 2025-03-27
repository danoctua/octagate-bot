import logging

from sqlalchemy.exc import NoResultFound
from telethon import events
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator

from core.actions.authorization import AuthorizationAction
from core.constants import REQUIRED_BOT_PRIVILEGES
from core.dtos.user import TelegramUserDTO
from core.services.chat import TelegramChatService
from core.services.chat.user import TelegramChatUserService
from core.services.db import DBService
from core.utils.events import ChatJoinRequestEventBuilder, ChatAdminChangeEventBuilder

logger = logging.getLogger(__name__)


__all__ = [
    "handle_chat_action",
    "handle_join_request",
    "handle_chat_participant_update",
]


# TODO: this handles events, but they could not be stored in case of the server restart
#  that will cause some join requests to be lost
#  This could be handled by recurrent/ad-hoc checks of the chat members (synchronization with the database)


async def handle_chat_action(event: events.ChatAction.Event):
    with DBService().db_session() as session:
        telegram_chat_service = TelegramChatService(session)
        if not telegram_chat_service.check_exists(event.chat_id):
            # Do not handle chats that are not in the database
            logger.debug(f"Chat {event.chat_id} does not exist in the database.")
            return

        logger.info(
            f"Chat action: {event.chat_id=!r} {event.user_id=!r} {event.action_message=!r}",
            extra={"event": event},
        )

        if not any(
            [event.user_joined, event.user_added, event.user_left, event.user_kicked]
        ):
            # To avoid handling other chat actions as they are not supported
            logger.debug(f"Chat action {event!r} is not handled.")
            return

        elif event.action_message:
            # To avoid handling multiple events twice (users are added or removed and the action message is sent)
            logger.debug(f"Chat action message {event!r} is not handled.")
            return

        authorization_action = AuthorizationAction(
            session, telethon_client=event.client
        )

        if event.user_joined or event.user_added:
            if event.added_by and event.added_by.is_self:
                # Do not handle actions made by the bot
                logger.debug(f"Action made by the bot {event.added_by.id!r}.")
                return

            logger.info(
                f"New chat members: {event.chat_id=!r} {event.user_ids=!r}",
                extra={"event": event},
            )
            await authorization_action.on_chat_members_in(
                chat_id=event.chat_id,
                users=[
                    TelegramUserDTO.from_telethon_user(user) for user in event.users
                ],
            )

        elif event.user_left or event.user_kicked:
            if event.kicked_by and event.kicked_by.is_self:
                # Do not handle actions made by the bot
                logger.debug(f"Action made by the bot {event.kicked_by.id!r}.")
                return

            logger.info(
                f"Chat members left/kicked: {event.chat_id=!r} {event.user_ids=!r}",
                extra={"event": event},
            )
            await authorization_action.on_chat_members_out(
                chat_id=event.chat_id,
                users=[
                    TelegramUserDTO.from_telethon_user(user) for user in event.users
                ],
            )


async def handle_join_request(event: ChatJoinRequestEventBuilder.Event):
    logger.debug(
        f"New join request: {event.chat_id=!r} {event.user_id=!r}",
    )
    with DBService().db_session() as session:
        authorization_action = AuthorizationAction(
            session, telethon_client=event.client
        )
        await authorization_action.on_join_request(
            telegram_user_id=event.user_id,
            chat_id=event.chat_id,
        )


async def handle_chat_participant_update(
    event: ChatAdminChangeEventBuilder.Event,
) -> None:
    # Chat ID received from the event is not prefixed with -100 for channels,
    #  so we need to prefix it if needed
    chat_id = int(
        f"-100{event.original_update.channel_id}"
        if event.original_update.channel_id > 0
        else event.original_update.channel_id
    )
    with DBService().db_session() as session:
        telegram_chat_service = TelegramChatService(session)
        try:
            chat = telegram_chat_service.get(chat_id)
        except NoResultFound:
            # Do not handle chats that are not in the database
            logger.debug(f"Chat {chat_id} does not exist in the database.")
            return

        logger.info("Handling chat participant update %s", event)

        if event.prev_participant.is_self:
            logger.info(
                "Bot user is managed: %d: %s",
                event.prev_participant.user_id,
                event.new_participant,
            )
            sufficient_privileges = all(
                [
                    getattr(event.new_participant.admin_rights, right)
                    for right in REQUIRED_BOT_PRIVILEGES
                ]
            )
            if not sufficient_privileges:
                if not chat.insufficient_privileges:
                    logger.warning(
                        "Insufficient permissions for the bot in chat %d", chat_id
                    )
                    telegram_chat_service.set_insufficient_privileges(chat_id=chat_id)
            else:
                if chat.insufficient_privileges:
                    logger.info(
                        "Sufficient permissions for the bot in chat %d", chat_id
                    )
                    telegram_chat_service.set_insufficient_privileges(
                        chat_id=chat_id, value=False
                    )
            return

        telegram_chat_user_service = TelegramChatUserService(db_session=session)
        try:
            target_user = telegram_chat_user_service.get(
                chat_id, event.new_participant.user_id
            )
        except NoResultFound:
            logger.warning(
                "User %d participation in the chat %d is not reflected in the database",
                event.new_participant.user_id,
                chat_id,
            )
            return

        if isinstance(
            event.prev_participant, ChannelParticipantAdmin
        ) and not isinstance(
            event.new_participant, (ChannelParticipantAdmin, ChannelParticipantCreator)
        ):
            logger.info(
                "Admin %d demoted in chat %d", event.prev_participant.user_id, chat_id
            )
            if target_user.is_admin:
                telegram_chat_user_service.demote_admin(
                    chat_id=chat_id, user_id=event.prev_participant.user_id
                )
            return

        elif not isinstance(
            event.prev_participant, ChannelParticipantAdmin
        ) and isinstance(event.new_participant, ChannelParticipantAdmin):
            logger.info(
                "Admin %d promoted in chat %d", event.new_participant.user_id, chat_id
            )
            if not target_user.is_admin:
                telegram_chat_user_service.promote_admin(
                    chat_id=chat_id, user_id=event.new_participant.user_id
                )
            return

        logger.debug("Participant update: %s", event.original_update)
