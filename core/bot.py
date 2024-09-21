import logging

from core.constants import POOL_TIMEOUT
from telegram.ext import (
    ApplicationBuilder,
    Application,
)

from core.handlers import handlers as message_handlers
from core.handlers.command import handlers as command_handlers
from core.handlers.callback import handlers as callback_handlers
from core.not_telegram_ext.limiter import NotAIORateLimiter
from core.not_telegram_ext.processor import MyUpdateProcessor
from core.settings import Config
from core.tasks.blockchain import fetch_jetton_holders

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
        self.configure_tasks()

    def configure_handlers(self):
        self.application.add_handlers(
            [
                # *backdoor_handlers,
                *message_handlers,
                *command_handlers,
                *callback_handlers,
            ]
        )

    def configure_tasks(self):
        self.application.job_queue.run_repeating(
            fetch_jetton_holders, interval=60 * 60, first=30 * 60
        )
        # self.application.job_queue.run_repeating(
        #     fetch_nft_owners, interval=60 * 60, first=2
        # )

    def start_polling(self):
        self.application.run_polling()

    def run_webhook(self):
        self.application.run_webhook(
            listen=Config.WEBHOOK_HOST,
            port=Config.WEBHOOK_PORT,
            url_path=Config.TELEGRAM_BOT_TOKEN,
            secret_token=Config.WEBHOOK_SECRET_KEY,
            webhook_url=f"{Config.WEBHOOK_URL}/{Config.TELEGRAM_BOT_TOKEN}",
        )


bot = NotBot(token=Config.TELEGRAM_BOT_TOKEN)
