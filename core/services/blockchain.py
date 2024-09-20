import asyncio
import logging
import time

from pytonapi import AsyncTonapi
from pytonapi.exceptions import TONAPIInternalServerError
from pytonapi.schema.jettons import JettonHolders, JettonHolder
from pytonapi.schema.nft import NftItems

from core.settings import Config


logger = logging.getLogger(__name__)


class BlockchainService:
    def __init__(self):
        self._tonapi = AsyncTonapi(api_key=Config.TON_API_KEY)

    async def get_all_jetton_holders(self, account_id: str) -> JettonHolders:
        """
        Get all jettons' holders.
        Adding some sleep to avoid hitting the rate limit.

        :param account_id: Account ID
        :return: :class:`JettonHolders`
        """
        jetton_holders: list[JettonHolder] = []
        offset, limit = 0, 1000
        previous_run_start: float | None = None
        result: JettonHolders | None = None

        while True:
            if (
                previous_run_start
                and (to_wait := (time.time() - previous_run_start)) <= 1
            ):
                await asyncio.sleep(to_wait)

            previous_run_start = time.time()
            try:
                result = await self._tonapi.jettons.get_holders(
                    account_id=account_id,
                    limit=limit,
                    offset=offset,
                )
            except TONAPIInternalServerError:
                logger.exception("Failed to fetch jetton holders", exc_info=True)
                previous_run_start = time.time()
                continue

            if len(result.addresses) == 0:
                break

            jetton_holders += result.addresses
            offset += limit

        return JettonHolders(addresses=jetton_holders, total=result.total)

    async def get_nft_items(self, account_id: str, offset: int, limit: int) -> NftItems:
        """
        Get NFT items.

        :param account_id: Account ID
        :param offset: offset
        :param limit: limit
        :return: list of NFT item addresses
        """
        result = await self._tonapi.nft.get_items_by_collection_address(
            account_id=account_id,
            limit=limit,
            offset=offset,
        )

        return result

    async def get_all_nft_items(self, account_id: str) -> NftItems:
        """
        Get all NFT items.

        :param account_id: Account ID
        :return: list of NFT item addresses
        """
        nft_items = []
        offset, limit = 0, 1000

        while True:
            result = await self._tonapi.nft.get_items_by_collection_address(
                account_id=account_id,
                limit=limit,
                offset=offset,
            )
            if len(result.items) == 0:
                break

            nft_items += result.nft_items
            offset += limit

        return NftItems(nft_items=nft_items, total=result.total)
