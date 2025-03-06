import asyncio
import logging

import click

from core.actions.chat import TelegramChatJettonAction
from core.services.chat import TelegramChatService
from core.services.db import DBService

logger = logging.getLogger(__name__)


async def link_telegram_chat_jetton(
    chat_id: int,
    jetton_address: str,
    threshold: int,
) -> None:
    with DBService().db_session() as db_session:
        chat = TelegramChatService(db_session).get(chat_id)
        action = TelegramChatJettonAction(db_session)
        action.create(
            slug=chat.slug,
            address_raw=jetton_address,
            threshold=threshold,
        )


@click.command()
@click.option("--chat-id", type=int, required=True)
@click.option("--jetton-address", type=str, required=True)
@click.option("--threshold", type=int, required=True)
def main(
    chat_id: int,
    jetton_address: str,
    threshold: int,
) -> None:
    """
    CLI command to load a Telegram chat.
    """
    asyncio.run(
        link_telegram_chat_jetton(
            chat_id=chat_id,
            jetton_address=jetton_address,
            threshold=threshold,
        )
    )
