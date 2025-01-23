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
from bot_ui.settings import bot_ui_settings


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
            .base_url(base_url=bot_ui_settings.telegram_api_base_url)
            .token(token)
            .concurrent_updates(MyUpdateProcessor(bot_ui_settings.concurrent_updates))
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
            listen=bot_ui_settings.webhook_host,
            port=bot_ui_settings.webhook_port,
            url_path=bot_ui_settings.telegram_bot_token,
            secret_token=bot_ui_settings.webhook_secret_key,
            webhook_url=bot_ui_settings.full_webhook_url,
        )


bot = NotBot(token=bot_ui_settings.telegram_bot_token)

if __name__ == "__main__":
    if not bot_ui_settings.is_active:
        logger.warning("Bot is not enabled")
    else:
        if bot_ui_settings.webhook_url:
            logger.info("Running webhook")
            bot.run_webhook()
        else:
            logger.info("Running polling")
            bot.start_polling()
