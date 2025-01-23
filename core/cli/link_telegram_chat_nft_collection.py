import asyncio
import logging

import click

from core.actions.chat import TelegramChatAction
from core.dtos.chat import TelegramChatNFTCollectionRuleDTO
from core.services.db import DBService

logger = logging.getLogger(__name__)


async def link_telegram_chat_nft_collection(
    chat_id: int,
    collection_address: str,
) -> None:
    with DBService().db_session() as db_session:
        telegram_chat_action = TelegramChatAction(db_session)
        telegram_chat_action.add_nft_collection_rule(
            TelegramChatNFTCollectionRuleDTO(
                chat_id=chat_id,
                collection_address=collection_address,
            )
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
