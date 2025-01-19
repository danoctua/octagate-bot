import asyncio

import click

from core.constants import NFT_LOGO_SUB_PATH, DEFAULT_NFT_LOGO_PATH
from core.services.blockchain import BlockchainService
from core.services.db import DBService
from core.services.nft import NftCollectionService
from core.utils.file import pick_best_preview, download_media


@click.command()
@click.argument("address")
def main(address: str) -> None:
    """
    CLI command to add a new NFT collection to the database.
    """

    blockchain_service = BlockchainService()
    nft_collection_data = asyncio.run(
        blockchain_service.get_nft_collection_info(address)
    )
    if nft_collection_data.previews:
        best_preview = pick_best_preview(nft_collection_data.previews)
        download_url = best_preview.url
        logo_path = download_media(
            download_url, name=address, subdirectory=NFT_LOGO_SUB_PATH
        )
    else:
        logo_path = DEFAULT_NFT_LOGO_PATH

    with DBService().db_session() as db_session:
        nft_service = NftCollectionService(db_session)
        nft_service.create_or_update(nft_collection_data, logo_path=logo_path)
