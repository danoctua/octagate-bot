import asyncio
import logging

from pytonapi.schema.jettons import JettonsBalances
from pytonapi.schema.nft import NftItems

from wallet_indexer.celery_app import (
    app,
    CELERY_WALLET_FETCH_QUEUE_NAME,
    CELERY_NOTICED_WALLETS_UPLOAD_QUEUE_NAME,
)
from wallet_indexer.indexers.tonapi import TonApiService
from core.services.db import DBService
from core.services.jetton import JettonService
from core.services.nft import NftCollectionService, NftItemService
from core.services.superredis import RedisService
from core.services.wallet import JettonWalletService

logger = logging.getLogger(__name__)


async def get_all_nfts_per_user(
    blockchain_service: TonApiService, address: str, nft_collections: list[str]
) -> NftItems:
    nft_items = []
    for collection_address in nft_collections:
        async for batch in blockchain_service.get_all_nft_items_for_user(
            wallet_address=address, collection_address=collection_address
        ):
            nft_items.extend(batch.nft_items)
    return NftItems(nft_items=nft_items)


@app.task(
    name="fetch-wallet-details",
    queue=CELERY_WALLET_FETCH_QUEUE_NAME,
)
def fetch_wallet_details(address: str) -> None:
    blockchain_service = TonApiService()

    jettons_balances: JettonsBalances = asyncio.run(
        blockchain_service.get_all_jetton_balances(address)
    )

    with DBService().db_session() as db_session:
        jetton_service = JettonService(db_session)
        whitelisted_jettons = jetton_service.get_whitelisted()

        jetton_wallet_service = JettonWalletService(db_session)
        jetton_wallet_service.bulk_create_or_update(
            jettons_balances, whitelisted_jettons, owner_address=address
        )
        logger.info(f"Jettons for {address!r} fetched.")

        nft_collection_service = NftCollectionService(db_session)
        whitelisted_nfts = nft_collection_service.get_whitelisted()
        whitelist_collection_addresses = [
            collection.address for collection in whitelisted_nfts
        ]

    nft_items: NftItems = asyncio.run(
        get_all_nfts_per_user(
            blockchain_service=blockchain_service,
            address=address,
            nft_collections=whitelist_collection_addresses,
        )
    )
    with DBService().db_session() as db_session:
        nft_service = NftItemService(db_session)
        nft_service.bulk_create_or_update(nft_items, whitelist_collection_addresses)
        logger.info(f"NFT items for {address!r} fetched.")


@app.task(
    name="load-noticed-wallets",
    queue=CELERY_NOTICED_WALLETS_UPLOAD_QUEUE_NAME,
)
def load_noticed_wallets():
    redis_service = RedisService(external=True)
    noticed_wallets = redis_service.get_unique_stream_items()
    for wallet in noticed_wallets:
        fetch_wallet_details.apply_async(args=(wallet,))

    app.send_task("load-noticed-wallets")
