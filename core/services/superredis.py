import redis

from core.settings import core_settings


class RedisService:
    def __init__(self, external: bool = False) -> None:
        if not external:
            self.client = redis.StrictRedis(
                host=core_settings.redis_host,
                port=core_settings.redis_port,
                db=core_settings.redis_db,
                decode_responses=True,
            )
        else:
            self.client = redis.StrictRedis(
                host=core_settings.redis_host,
                port=core_settings.redis_port,
                db=core_settings.redis_transaction_db,
                decode_responses=True,
            )

    def get(self, key: str) -> str:
        return self.client.get(key)

    def set(self, key: str, value: str, ex: int | None = None) -> None:
        self.client.set(key, value, ex=ex)

    def set_all(self, data: dict, ex: int | None = None) -> None:
        pipeline = self.client.pipeline()
        for key, value in data.items():
            pipeline.set(key, value, ex=ex)
        pipeline.execute()

    def delete(self, key: str) -> str:
        return self.client.delete(key)

    def get_stream_items(self):
        return self.client.xread({core_settings.redis_transaction_stream_name: "0-0"})

    def get_unique_stream_items(self):
        return set(self.get_stream_items())
