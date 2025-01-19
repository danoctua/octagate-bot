import asyncio
import logging

from pytonapi.schema.jettons import JettonsBalances
from pytonapi.schema.nft import NftItems

from core.celery_app import (
    app,
    CELERY_WALLET_FETCH_QUEUE_NAME,
    CELERY_NOTICED_WALLETS_UPLOAD_QUEUE_NAME,
)
from core.services.blockchain import BlockchainService
from core.services.db import DBService
from core.services.jetton import JettonService
from core.services.nft import NftCollectionService, NftItemService
from core.services.superredis import RedisService
from core.services.wallet import WalletService


logger = logging.getLogger(__name__)


async def get_all_nfts_per_user(
    blockchain_service: BlockchainService, address: str
) -> NftItems:
    nft_items = []
    async for batch in blockchain_service.get_all_nft_items_for_user(
        wallet_address=address
    ):
        nft_items.extend(batch.nft_items)
    return NftItems(nft_items=nft_items)


@app.task(
    name="fetch-wallet-details",
    queue=CELERY_WALLET_FETCH_QUEUE_NAME,
)
def fetch_wallet_details(address: str) -> None:
    blockchain_service = BlockchainService()

    jettons_balances: JettonsBalances = asyncio.run(
        blockchain_service.get_all_jetton_balances(address)
    )

    with DBService().db_session() as db_session:
        jetton_service = JettonService(db_session)
        whitelisted_jettons = jetton_service.get_whitelisted()

        wallet_service = WalletService(db_session)
        wallet_service.create_or_update_jettons_balances(
            jettons_balances, whitelisted_jettons, owner_address=address
        )
        logger.info(f"Jettons for {address!r} fetched.")

    nft_items: NftItems = asyncio.run(
        get_all_nfts_per_user(blockchain_service=blockchain_service, address=address)
    )
    with DBService().db_session() as db_session:
        nft_collection_service = NftCollectionService(db_session)
        whitelisted_nfts = nft_collection_service.get_whitelisted()
        nft_service = NftItemService(db_session)
        nft_service.bulk_create_or_update(nft_items, whitelisted_nfts)
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
