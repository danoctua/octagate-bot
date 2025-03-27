import logging

from telethon import events

from core.actions.authorization import AuthorizationAction
from core.dtos.user import TelegramUserDTO
from core.services.chat import TelegramChatService
from core.services.db import DBService
from core.utils.events import ChatJoinRequestEvent

logger = logging.getLogger(__name__)


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


async def handle_join_request(event: ChatJoinRequestEvent.Event):
    # Your logic here - approve/deny requests
    logger.info(
        f"New join request: {event.chat_id=!r} {event.user_id=!r}",
        extra={"event": event},
    )
    with DBService().db_session() as session:
        authorization_action = AuthorizationAction(
            session, telethon_client=event.client
        )
        await authorization_action.on_join_request(
            telegram_user_id=event.user_id,
            chat_id=event.chat_id,
        )


# TODO: handle admin demotion and promotion
# @events.register(events.Raw(UpdateChannelParticipant))
# async def _(event: UpdateChannelParticipant):
#     if isinstance(
#         event.prev_participant,
#         ChannelParticipantAdmin
#     ) and not isinstance(
#         event.new_participant,
#         (ChannelParticipantAdmin,ChannelParticipantCreator)
#     ):
#         # Demote admin ...
#         ...
#     elif isinstance(
#         event.prev_participant,ChannelParticipantAdmin
#     ) and isinstance(
#         event.new_participant,ChannelParticipantAdmin
#     ): # You may check new admin rights using event.new_participant.admin_rights ( ChatAdminRights )
#         pass # As I don't want to check admin rights and my point is just person being an admin.
#     elif isinstance(event.new_participant,ChannelParticipantAdmin):
#         # We do promotion ( You might add your checking rights conditions , now this condition will be passed only if he wasn't supposed to be demoted and becomes an admin )
#         ...
