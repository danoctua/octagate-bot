from pytonconnect import TonConnect
from pytonconnect.storage import IStorage

from core.services.superredis import RedisService
from core.settings import core_settings


def get_connector(chat_id: int) -> TonConnect:
    return TonConnect(
        core_settings.tc_manifest_url, storage=TCRStorage(chat_id=chat_id)
    )


class TCRStorage(IStorage):
    # TODO deprecate after moving to FE-based storage for TON Connect
    """TON Connect Redis storage implementation."""

    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.redis_service = RedisService()

    def _get_key(self, key: str):
        return str(self.chat_id) + key

    async def set_item(self, key: str, value: str):
        self.redis_service.set(key=self._get_key(key), value=value)

    async def get_item(self, key: str, default_value: str = None):
        value = self.redis_service.get(key=self._get_key(key))
        return value or default_value

    async def remove_item(self, key: str):
        self.redis_service.client.delete(self._get_key(key))
