import logging

from pytonconnect import TonConnect
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from core.renderers import connected_wallet_welcome_renderer, start_renderer
from core.services.db import DBService
from core.services.user import UserService

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.Logger(__name__)


async def start_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE,
) -> None:
    return await start_renderer(update, context)
