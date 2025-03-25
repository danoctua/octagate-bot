import asyncio
import logging

from community_manager.handlers import telethon_service

import community_manager.handlers.chat  # noqa


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Starting Octagate Bot Telethon client.")
    asyncio.run(telethon_service.start())
    telethon_service.client.run_until_disconnected()
