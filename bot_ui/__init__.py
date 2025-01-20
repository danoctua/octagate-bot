import logging

from telegram import Update
from telegram.ext import Application, ApplicationBuilder

from bot_ui.handlers import handlers as message_handlers
from bot_ui.handlers.callback import handlers as callback_handlers
from bot_ui.handlers.command import handlers as command_handlers
from bot_ui.handlers.error import error_handler
from bot_ui.not_telegram_ext.limiter import NotAIORateLimiter
from bot_ui.not_telegram_ext.processor import MyUpdateProcessor
from core.constants import POOL_TIMEOUT
from core.settings import Config
from core.services.db import DBService


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class NotBot:
    def __init__(self, token: str) -> None:
        self.__token = token
        rate_limiter = NotAIORateLimiter(
            write_max_rate=30,
            write_time_period=1,
            overall_max_rate=60,
            overall_time_period=1,
            # max_retries=1,
        )
        self.application: Application = (
            ApplicationBuilder()
            .pool_timeout(POOL_TIMEOUT)
            .base_url(base_url=Config.TELEGRAM_API_BASE_URL)
            .token(token)
            .concurrent_updates(MyUpdateProcessor(Config.CONCURRENT_UPDATES))
            .rate_limiter(rate_limiter)
            .build()
        )
        self.configure_handlers()

    def configure_handlers(self):
        self.application.add_handlers(
            [
                # *backdoor_handlers,
                *message_handlers,
                *command_handlers,
                *callback_handlers,
            ]
        )
        self.application.add_error_handler(error_handler)

    def start_polling(self):
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    def run_webhook(self):
        self.application.run_webhook(
            listen=Config.WEBHOOK_HOST,
            port=Config.WEBHOOK_PORT,
            url_path=Config.TELEGRAM_BOT_TOKEN,
            secret_token=Config.WEBHOOK_SECRET_KEY,
            webhook_url=f"{Config.WEBHOOK_URL}/{Config.TELEGRAM_BOT_TOKEN}",
        )


bot = NotBot(token=Config.TELEGRAM_BOT_TOKEN)

if __name__ == "__main__":
    DBService.create_tables()
    if Config.WEBHOOK_URL:
        logger.info("Running webhook")
        bot.run_webhook()
    else:
        logger.info("Running polling")
        bot.start_polling()
