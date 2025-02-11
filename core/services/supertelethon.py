import logging
from typing import AsyncGenerator

from telethon import TelegramClient
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import User as TelethonUser, Channel, ChatInviteExported

from core.constants import TELETHON_SESSION_PATH, CHAT_LOGO_PATH, DEFAULT_CHAT_LOGO_PATH
from core.settings import core_settings


logger = logging.getLogger(__name__)


class TelethonService:
    def __init__(self):
        self.client = TelegramClient(
            TELETHON_SESSION_PATH,
            core_settings.telegram_app_id,
            core_settings.telegram_app_hash,
        )

    async def start(self) -> None:
        await self.client.start(bot_token=core_settings.telegram_bot_token)

    async def stop(self) -> None:
        await self.client.disconnect()

    async def get_chat(self, chat_id: int) -> Channel:
        return await self.client.get_entity(chat_id)

    async def get_user(self, telegram_user_id: int) -> TelethonUser:
        return await self.client.get_entity(telegram_user_id)

    async def get_participants(
        self, chat_id: int
    ) -> AsyncGenerator[TelethonUser, None]:
        async for participant in self.client.iter_participants(chat_id):
            yield participant

    async def get_invite_link(self, chat: Channel) -> ChatInviteExported:
        invite_link = await self.client(
            ExportChatInviteRequest(
                peer=chat,
                title="Octagate invite link",
                request_needed=True,
            )
        )
        return invite_link

    async def download_profile_photo(self, entity: Channel) -> str:
        if not entity.photo:
            logger.info(
                f"Chat {entity.id!r} does not have a logo. Using the default one."
            )
            return DEFAULT_CHAT_LOGO_PATH

        logo_path = f"{entity.id}.jpg"

        with open(CHAT_LOGO_PATH / logo_path, "wb") as f:
            await self.client.download_profile_photo(entity, f)

        return logo_path

    async def promote_user(
        self, chat_id: int, telegram_user_id: int, custom_title: str
    ) -> None:
        chat = await self.get_chat(chat_id)
        user = await self.get_user(telegram_user_id)
        await self.client.edit_admin(
            entity=chat,
            user=user,
            is_admin=True,
            title=custom_title,
        )

    async def demote_user(
        self,
        chat_id: int,
        telegram_user_id: int,
    ) -> None:
        chat = await self.get_chat(chat_id)
        user = await self.get_user(telegram_user_id)
        await self.client.edit_admin(
            entity=chat,
            user=user,
            is_admin=False,
        )

    async def kick_chat_member(self, chat_id: int, telegram_user_id: int) -> None:
        chat = await self.get_chat(chat_id)
        user = await self.get_user(telegram_user_id)
        await self.client.kick_participant(chat, user)
