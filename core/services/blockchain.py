import asyncio
import time

from pytonapi import AsyncTonapi
from pytonapi.schema.jettons import JettonHolders, JettonHolder

from core.settings import Config


class BlockchainService:
    def __init__(self):
        self._tonapi = AsyncTonapi(api_key=Config.TON_API_KEY)

    async def get_all_holders(self, account_id: str) -> JettonHolders:
        """
        Get all jettons' holders.
        Adding some sleep to avoid hitting the rate limit.

        :param account_id: Account ID
        :return: :class:`JettonHolders`
        """
        jetton_holders: list[JettonHolder] = []
        offset, limit = 0, 1000
        previous_run_start: float | None = None

        while True:
            if (
                previous_run_start
                and (to_wait := (time.time() - previous_run_start)) <= 1
            ):
                await asyncio.sleep(to_wait)

            previous_run_start = time.time()
            result = await self._tonapi.jettons.get_holders(
                account_id=account_id,
                limit=limit,
                offset=offset,
            )
            if len(result.addresses) == 0:
                break

            jetton_holders += result.addresses
            offset += limit

        return JettonHolders(addresses=jetton_holders, total=result.total)
