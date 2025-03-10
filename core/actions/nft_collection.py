import logging

from sqlalchemy.orm import Session

from core.dtos.resource import NftCollectionDTO
from core.actions.base import BaseAction
from core.constants import NFT_LOGO_SUB_PATH, DEFAULT_NFT_LOGO_PATH
from core.services.nft import NftCollectionService
from core.utils.file import pick_best_preview, download_media
from wallet_indexer.indexers.tonapi import TonApiService

logger = logging.getLogger(__name__)


class NftCollectionAction(BaseAction):
    def __init__(self, db_session: Session) -> None:
        super().__init__(db_session)
        self.nft_collection_service = NftCollectionService(db_session)

    def get_all(self, whitelisted_only: bool) -> list[NftCollectionDTO]:
        nft_collections = self.nft_collection_service.get_all(
            whitelisted_only=whitelisted_only
        )
        return [
            NftCollectionDTO.from_orm(nft_collection)
            for nft_collection in nft_collections
        ]

    def get(self, address_raw: str) -> NftCollectionDTO:
        nft_collection = self.nft_collection_service.get(address_raw)
        return NftCollectionDTO.from_orm(nft_collection)

    async def create(self, address_raw: str) -> NftCollectionDTO:
        blockchain_service = TonApiService()
        nft_collection_data = await blockchain_service.get_nft_collection_info(
            address_raw
        )
        if nft_collection_data.previews:
            best_preview = pick_best_preview(nft_collection_data.previews)
            download_url = best_preview.url
            logo_path = download_media(
                download_url, name=address_raw, subdirectory=NFT_LOGO_SUB_PATH
            )
        else:
            logo_path = DEFAULT_NFT_LOGO_PATH

        nft_collection = self.nft_collection_service.create_or_update(
            nft_collection_data, logo_path=logo_path
        )
        return NftCollectionDTO.from_orm(nft_collection)

    async def update(self, address_raw: str, is_enabled: bool) -> NftCollectionDTO:
        nft_collection = self.nft_collection_service.update_status(
            address_raw, is_enabled
        )
        return NftCollectionDTO.from_orm(nft_collection)
