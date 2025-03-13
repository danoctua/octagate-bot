from collections import defaultdict
from typing import Self, Any

from pydantic import BaseModel
from pytonapi.utils import raw_to_userfriendly
from pytonapi.schema.nft import NftItem as TONNftItem

from core.models.blockchain import Jetton, NFTCollection


class JettonDTO(BaseModel):
    address: str
    name: str
    description: str | None
    symbol: str
    logo_path: str | None
    is_enabled: bool

    @classmethod
    def from_orm(cls, obj: Jetton) -> Self:
        return cls(
            address=raw_to_userfriendly(obj.address),
            name=obj.name,
            description=obj.description,
            symbol=obj.symbol,
            logo_path=obj.logo_path,
            is_enabled=obj.is_enabled,
        )


class NftItemAttributeDTO(BaseModel):
    trait_type: str
    value: Any


class NftItemMetadataDTO(BaseModel):
    attributes: list[NftItemAttributeDTO]

    @classmethod
    def from_nft_item(cls, nft_item: TONNftItem) -> Self:
        return cls(
            attributes=[
                NftItemAttributeDTO(
                    trait_type=trait["trait_type"],
                    value=trait["value"],
                )
                # NFT item could have no attributes
                for trait in nft_item.metadata.get("attributes", [])
            ]
        )


class NftCollectionAttributeDTO(BaseModel):
    trait_type: str
    values: list[Any]


class NftCollectionMetadataDTO(BaseModel):
    attributes: list[NftCollectionAttributeDTO]

    @classmethod
    def from_items_metadata(cls, items_metadata: list[NftItemMetadataDTO]) -> Self:
        combined = defaultdict(set)
        for item_metadata in items_metadata:
            for attribute in item_metadata.attributes:
                combined[attribute.trait_type].add(attribute.value)

        return cls(
            attributes=[
                NftCollectionAttributeDTO(
                    trait_type=trait_type,
                    values=sorted(values),
                )
                for trait_type, values in combined.items()
            ]
        )


class NftCollectionDTO(BaseModel):
    address: str
    name: str
    description: str | None
    logo_path: str | None
    is_enabled: bool
    blockchain_metadata: NftCollectionMetadataDTO | None = None

    @classmethod
    def from_orm(cls, obj: NFTCollection) -> Self:
        return cls(
            address=raw_to_userfriendly(obj.address),
            name=obj.name,
            description=obj.description,
            logo_path=obj.logo_path,
            is_enabled=obj.is_enabled,
            blockchain_metadata=(
                NftCollectionMetadataDTO.model_validate(obj.blockchain_metadata)
                if obj.blockchain_metadata
                else None
            ),
        )
