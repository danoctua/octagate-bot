import logging

from core.bot import bot
from core.services.db import DBService
from core.settings import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    DBService.create_tables()
    if Config.WEBHOOK_URL:
        logger.info("Running webhook")
        bot.run_webhook()
    else:
        logger.info("Running polling")
        bot.start_polling()
