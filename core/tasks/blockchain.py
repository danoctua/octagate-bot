import logging

from pytonapi.async_tonapi import AsyncTonapi
from telegram.ext import ContextTypes

from core.settings import Config
from core.services.db import DBService
from core.services.wallet import WalletService


logger = logging.getLogger(__name__)


async def fetch_jetton_holders(context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        logger.info("Fetching jetton holders")
        # Fetch jetton holders from the blockchain
        tonapi = AsyncTonapi(api_key=Config.TON_API_KEY)
        holders = await tonapi.jettons.get_all_holders(Config.TARGET_JETTON_MASTER)
        logger.info(f"Found {holders.total} holders")
        with DBService().db_session() as db_session:
            wallet_service = WalletService(db_session)
            wallet_service.bulk_update_jetton_holders(holders)
        logger.info("Jetton holders fetched and saved. Found %s holders", holders.total)
    except Exception:
        await context.bot.send_message(
            chat_id=Config.ADMIN_IDS[0],
            text="Failed to fetch jetton holders from the blockchain",
        )
        raise  # Reraise the exception to logs
