import logging

from pytonapi.schema.nft import NftCollection
from sqlalchemy.exc import NoResultFound

from core.models.blockchain import NFTCollection
from core.services.base import BaseService


logger = logging.getLogger(__name__)


class NftService(BaseService):
    def create(self, nft_collection: NftCollection, logo_path: str) -> NFTCollection:
        nft = NFTCollection(
            address=nft_collection.address.to_raw(),
            name=nft_collection.metadata["name"],
            description=nft_collection.metadata["description"],
            logo_path=logo_path,
        )
        self.db_session.add(nft)
        self.db_session.commit()
        logger.info(f"NFT Collection {nft.name!r} created.")
        return nft

    def update(
        self, nft_collection: NftCollection, nft: NFTCollection, logo_path: str
    ) -> NFTCollection:
        nft.name = nft_collection.metadata["name"]
        nft.description = nft_collection.metadata["description"]
        nft.logo_path = logo_path
        self.db_session.commit()
        logger.info(f"NFT Collection {nft.name!r} updated.")
        return nft

    def create_or_update(
        self, nft_collection: NftCollection, logo_path: str
    ) -> NFTCollection:
        try:
            nft = self.get(address=nft_collection.address.to_raw())
            return self.update(nft_collection, nft, logo_path=logo_path)
        except NoResultFound:
            logger.info(
                f"No NFT Collection for address {nft_collection.address!r} found. Creating new NFT Collection."
            )
            return self.create(nft_collection, logo_path=logo_path)

    def get(self, address: str) -> NFTCollection:
        return (
            self.db_session.query(NFTCollection)
            .filter(NFTCollection.address == address)
            .one()
        )
