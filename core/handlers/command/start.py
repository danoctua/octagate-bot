import logging

from telegram import Update
from telegram.ext import ContextTypes

from core.renderers import start_renderer

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.Logger(__name__)


async def start_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    return await start_renderer(update, context)
