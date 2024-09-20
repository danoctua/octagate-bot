import logging

from telegram.ext import ContextTypes

from core.services.blockchain import BlockchainService
from core.services.user import UserService
from core.settings import Config
from core.services.db import DBService
from core.services.wallet import WalletService
from core.utils.authorization import get_telegram_chat_admins, promote_user, demote_user

logger = logging.getLogger(__name__)


async def fetch_jetton_holders(context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        logger.info("Fetching jetton holders")
        # Fetch jetton holders from the blockchain
        holders = await BlockchainService().get_all_jetton_holders(
            Config.TARGET_JETTON_MASTER
        )
        logger.info(f"Found {holders.total} holders")
        with DBService().db_session() as db_session:
            wallet_service = WalletService(db_session)
            wallet_service.bulk_update_jetton_holders(holders)
        logger.info("Jetton holders fetched and saved. Found %s holders", holders.total)
        context.application.job_queue.run_once(sanity_admins_check)
    except Exception:
        logger.exception("Failed to fetch jetton holders")
        raise  # Reraise the exception to logs


async def sanity_admins_check(context: ContextTypes.DEFAULT_TYPE) -> None:
    admins = await get_telegram_chat_admins(context)
    admin_ids = [admin.user.id for admin in admins]
    logger.info("Checking sanity of admins")
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        users = user_service.get_all_prefetched()
        for user in users:
            # Promote user if they are a whale and not an admin
            if user.wallet and user.wallet.jetton_wallet:
                if user.wallet.jetton_wallet.is_whale:
                    if user.telegram_id not in admin_ids:
                        await promote_user(context, user=user)
                    continue
            # Demote user if they are an admin and not a whale
            if user.telegram_id in admin_ids:
                await demote_user(context, telegram_id=user.telegram_id)
    logger.info("Sanity of admins checked")
