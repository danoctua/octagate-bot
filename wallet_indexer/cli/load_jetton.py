import asyncio

import click
from pytonapi.schema.jettons import JettonInfo

from core.constants import JETTON_LOGO_SUB_PATH, DEFAULT_JETTON_LOGO_PATH
from wallet_indexer.indexers.tonapi import TonApiService
from core.services.db import DBService
from core.services.jetton import JettonService
from core.utils.file import download_media


@click.command()
@click.argument("address")
def main(address: str) -> None:
    """
    CLI command to add a token to the database.
    """

    blockchain_service = TonApiService()
    jetton_info: JettonInfo = asyncio.run(blockchain_service.get_jetton_info(address))

    jetton_logo = jetton_info.metadata.image

    if jetton_logo:
        logo_name = download_media(
            jetton_logo, subdirectory=JETTON_LOGO_SUB_PATH, name=address
        )
    else:
        logo_name = DEFAULT_JETTON_LOGO_PATH

    with DBService().db_session() as db_session:
        jetton_service = JettonService(db_session)
        jetton_service.create_or_update(jetton_info, logo_path=logo_name)
