import logging
from typing import Coroutine

from telegram import Update
from telegram.ext import BaseUpdateProcessor

from core.utils.cache import (
    format_request_cache_key_value,
    check_user_action_cache,
    add_user_action_cache,
)

logger = logging.getLogger(__name__)


class MyUpdateProcessor(BaseUpdateProcessor):
    async def do_process_update(self, update: Update, coroutine: Coroutine) -> None:
        cache_key, cache_value = format_request_cache_key_value(update=update)
        if cache_key and cache_value:
            if await check_user_action_cache(key=cache_key, value=cache_value):
                logger.debug(
                    "Duplicated requests for `%s`: %s. Skipping...",
                    cache_key,
                    cache_value[:20].decode(),
                )
                return

            await add_user_action_cache(key=cache_key, value=cache_value)

        await coroutine

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass
