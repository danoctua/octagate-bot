import redis

from core.settings import Config


class RedisService:
    def __init__(self, external: bool = False) -> None:
        if not external:
            self.client = redis.StrictRedis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                decode_responses=True,
            )
        else:
            self.client = redis.StrictRedis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_TRANSACTION_DB,
                decode_responses=True,
            )

    def get(self, key: str) -> str:
        return self.client.get(key)

    def set(self, key: str, value: str, ex: int | None = None) -> None:
        self.client.set(key, value, ex=ex)

    def delete(self, key: str) -> str:
        return self.client.delete(key)

    def get_stream_items(self):
        return self.client.xread({Config.REDIS_TRANSACTION_STREAM_NAME: "0-0"})

    def get_unique_stream_items(self):
        return set(self.get_stream_items())
