import asyncio

import click

from core.dtos.user import TelegramUserDTO
from core.services.chat import TelegramChatService, TelegramChatUserService
from core.services.db import DBService
from core.services.supertelethon import TelethonService
from core.services.user import UserService


async def load_telegram_chat(chat_id: int) -> None:
    telethon_service = TelethonService()
    await telethon_service.start()

    chat = await telethon_service.get_chat(chat_id)
    if not chat.admin_rights.change_info:
        click.echo(
            "Please add the bot to the chat with privileges to at least change info right.",
            err=True,
        )
        exit(1)

    click.echo("Loading chat logo...")
    logo_path = await telethon_service.download_profile_photo(chat)
    with DBService().db_session() as db_session:
        telegram_chat_service = TelegramChatService(db_session)
        telegram_chat = telegram_chat_service.create_or_update(
            chat_id=chat_id, entity=chat, logo_path=logo_path
        )
        if not telegram_chat.invite_link:
            click.echo("Creating chat invite link...")
            invite_link = await telethon_service.get_invite_link(chat)
            telegram_chat_service.refresh_invite_link(chat_id, invite_link.link)
        else:
            click.echo("Chat invite link already exists...")

        user_service = UserService(db_session)
        telegram_chat_user_service = TelegramChatUserService(db_session)
        click.echo("Loading chat participants...")
        async for participant_user in telethon_service.get_participants(chat_id):
            if participant_user.bot:
                continue

            user = user_service.create_or_update(
                TelegramUserDTO(
                    id=participant_user.id,
                    first_name=participant_user.first_name,
                    last_name=participant_user.last_name,
                    username=participant_user.username,
                    is_premium=participant_user.premium or False,
                    language_code=participant_user.lang_code,
                )
            )
            telegram_chat_user_service.create_or_update(
                chat_id=chat_id,
                user_id=user.id,
                is_admin=hasattr(participant_user.participant, "admin_rights"),
                is_whale_admin=False,
            )
    click.echo("Chat loaded successfully.")


@click.command()
@click.argument("chat_id", type=int)
def main(chat_id: int) -> None:
    """
    CLI command to load a Telegram chat.
    """
    asyncio.run(load_telegram_chat(chat_id))
