import asyncio
import logging

import click

from core.actions.chat import TelegramChatAction
from core.dtos.chat import TelegramChatJettonRuleDTO
from core.services.db import DBService

logger = logging.getLogger(__name__)


async def link_telegram_chat_jetton(
    chat_id: int,
    jetton_address: str,
    threshold: int,
    whale_threshold: int,
    whale_label_template: str,
) -> None:
    with DBService().db_session() as db_session:
        telegram_chat_action = TelegramChatAction(db_session)
        telegram_chat_action.add_jetton_rule(
            TelegramChatJettonRuleDTO(
                chat_id=chat_id,
                jetton_address=jetton_address,
                threshold=threshold,
                whale_threshold=whale_threshold,
                whale_label_template=whale_label_template,
            )
        )


@click.command()
@click.option("--chat-id", type=int, required=True)
@click.option("--jetton-address", type=str, required=True)
@click.option("--threshold", type=int, required=True)
@click.option("--whale-threshold", type=int, required=False, default=None)
@click.option("--whale-label-template", type=str, required=False, default=None)
def main(
    chat_id: int,
    jetton_address: str,
    threshold: int,
    whale_threshold: int,
    whale_label_template: str,
) -> None:
    """
    CLI command to load a Telegram chat.
    """
    asyncio.run(
        link_telegram_chat_jetton(
            chat_id=chat_id,
            jetton_address=jetton_address,
            threshold=threshold,
            whale_threshold=whale_threshold,
            whale_label_template=whale_label_template,
        )
    )
