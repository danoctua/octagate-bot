import logging

from telegram import Update
from telegram.error import Forbidden
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.

    if isinstance(context.error, Forbidden):
        logger.warning("Forbidden error: %s", context.error.message)
        return

    logger.exception("Exception while handling an update:", exc_info=context.error)
