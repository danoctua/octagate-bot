import redis
from telegram import Update

from core.settings import Config

DEFAULT_EXPIRATION_SECONDS = 10


redis_client = redis.asyncio.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0)


def format_response_cache_key_value(
    command: str, kwargs: dict
) -> tuple[str | None, bytes | None]:
    if not kwargs or not (chat_id := kwargs.get("chat_id")):
        return None, None

    return f"response:{chat_id}", f"{command}{kwargs}".encode("utf-8")


def format_request_cache_key_value(
    update: Update,
) -> tuple[str, bytes] | tuple[None, None]:
    if not update or not update.effective_chat.id:
        return None, None

    if update.callback_query:
        return f"callback:{update.effective_chat.id}", str(
            update.callback_query.data
        ).encode("utf-8")

    elif update.message:
        return f"message:{update.effective_chat.id}", str(update.message.text).encode(
            "utf-8"
        )

    return None, None


async def add_user_action_cache(key: str, value: bytes):
    await redis_client.setex(key, DEFAULT_EXPIRATION_SECONDS, value)


async def check_user_action_cache(key: str, value: bytes) -> bool:
    return await redis_client.getex(key) == value
