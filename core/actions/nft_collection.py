import asyncio
import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.dtos.resource import NftCollectionDTO
from core.actions.base import BaseAction
from core.constants import NFT_LOGO_SUB_PATH, DEFAULT_NFT_LOGO_PATH
from core.services.nft import NftCollectionService
from core.services.superredis import RedisService
from core.utils.file import pick_best_preview, download_media
from indexer.indexers.tonapi import TonApiService

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

        blockchain_metadata = await blockchain_service.parse_nft_collection_metadata(
            address_raw
        )

        nft_collection = self.nft_collection_service.create_or_update(
            nft_collection_data,
            logo_path=logo_path,
            blockchain_metadata=blockchain_metadata,
        )
        return NftCollectionDTO.from_orm(nft_collection)

    async def _refresh_metadata(self, task_id: str, address_raw: str) -> None:
        blockchain_service = TonApiService()

        blockchain_metadata = await blockchain_service.parse_nft_collection_metadata(
            address_raw, partial=False
        )
        self.nft_collection_service.update_metadata(
            address=address_raw, blockchain_metadata=blockchain_metadata
        )
        redis_service = RedisService()
        redis_service.pop_task_status(task_id)

    async def refresh_metadata(self, address_raw: str) -> None:
        redis_service = RedisService()
        task_id = f"refresh_metadata_{address_raw}"
        if task_status := redis_service.check_task_status(task_id):
            # redis_service.pop_task_status(task_id)
            raise HTTPException(
                status_code=409,
                detail=f"Task is already in progress. Status: {task_status}",
            )
        redis_service.set_task_status(task_id, "in_progress")

        asyncio.create_task(self._refresh_metadata(task_id, address_raw))

    async def update(self, address_raw: str, is_enabled: bool) -> NftCollectionDTO:
        nft_collection = self.nft_collection_service.update_status(
            address_raw, is_enabled
        )
        return NftCollectionDTO.from_orm(nft_collection)
