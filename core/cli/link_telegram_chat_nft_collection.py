import asyncio
import logging

import click

from core.actions.chat.rule.blockchain import TelegramChatNFTCollectionAction
from core.services.chat import TelegramChatService
from core.services.db import DBService

logger = logging.getLogger(__name__)


async def link_telegram_chat_nft_collection(
    chat_id: int,
    collection_address: str,
) -> None:
    with DBService().db_session() as db_session:
        telegram_chat_service = TelegramChatService(db_session)
        chat = telegram_chat_service.get(chat_id=chat_id)
        telegram_chat_nft_collection_action = TelegramChatNFTCollectionAction(
            db_session
        )
        telegram_chat_nft_collection_action.create(
            slug=chat.slug, address_raw=collection_address, threshold=1
        )


@click.command()
@click.option("--chat-id", type=int, required=True)
@click.option("--collection-address", type=str, required=True)
def main(
    chat_id: int,
    collection_address: str,
) -> None:
    """
    CLI command to load a Telegram chat.
    """
    asyncio.run(
        link_telegram_chat_nft_collection(
            chat_id=chat_id,
            collection_address=collection_address,
        )
    )
