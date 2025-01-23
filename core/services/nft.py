import logging

from pytonapi.schema.nft import NftCollection, NftItem as TONNftItem, NftItems
from sqlalchemy.exc import NoResultFound

from core.models.blockchain import NFTCollection, NftItem
from core.services.base import BaseService


logger = logging.getLogger(__name__)


class NftCollectionService(BaseService):
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

    def get_whitelisted(self) -> list[NFTCollection]:
        return (
            self.db_session.query(NFTCollection)
            .filter(NFTCollection.is_enabled.is_(True))
            .all()
        )


class NftItemService(BaseService):
    def _create(self, nft_item: TONNftItem) -> NftItem:
        nft = NftItem(
            address=nft_item.address.to_raw(),
            owner_address=nft_item.owner.address.to_raw(),
            collection_address=nft_item.collection.address.to_raw(),
        )
        self.db_session.add(nft)
        logger.info(f"NFT Item {nft.address!r} created.")
        return nft

    def _update(self, nft_item: TONNftItem, nft: NftItem) -> NftItem:
        """The only updatable field is the owner address."""
        nft.owner_address = nft_item.owner.address.to_raw()
        self.db_session.add(nft)
        logger.info(f"NFT Item {nft.address!r} updated.")
        return nft

    def create_or_update(self, nft_item: TONNftItem) -> NftItem:
        try:
            nft = self.get(address=nft_item.address.to_raw())
            return self._update(nft_item, nft)
        except NoResultFound:
            logger.info(
                f"No NFT Item for address {nft_item.address!r} found. Creating new NFT Item."
            )
            return self._create(nft_item)

    def get(self, address: str) -> NftItem:
        return self.db_session.query(NftItem).filter(NftItem.address == address).one()

    def get_all(
        self, owner_address: str | None = None, collection_address: str | None = None
    ) -> list[NftItem]:
        query = self.db_session.query(NftItem)
        if owner_address:
            query = query.filter(NftItem.owner_address == owner_address)

        if collection_address:
            query = query.filter(NftItem.collection_address == collection_address)
        return query.all()

    def bulk_create_or_update(
        self, nft_items: NftItems, whitelist_collection_addresses: list[str]
    ) -> list[NftItem]:
        created_or_updated_nfts = []
        for nft_item in nft_items.nft_items:
            if (
                not nft_item.collection
                or nft_item.collection.address.to_raw()
                not in whitelist_collection_addresses
            ):
                continue

            created_or_updated_nfts.append(self.create_or_update(nft_item))
        self.db_session.commit()
        return created_or_updated_nfts
