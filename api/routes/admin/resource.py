import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from pytonapi.exceptions import TONAPINotFoundError
from pytonapi.utils import userfriendly_to_raw
from sqlalchemy.orm import Session

from api.deps import get_db_session
from api.pos.blockchain import (
    CreateJettonCPO,
    UpdateJettonCPO,
    GetJettonCPO,
    CreateNftCollectionCPO,
    GetNftCollectionCPO,
    UpdateNftCollectionCPO,
    JettonFDO,
    NftCollectionFDO,
)
from api.pos.common import StatusFDO
from core.actions.jetton import JettonAction
from core.actions.nft_collection import NftCollectionAction
from core.services.jetton import JettonService

logger = logging.getLogger(__name__)

admin_resource_router = APIRouter(prefix="/resources", deprecated=True)


@admin_resource_router.get("/jettons")
async def get_jettons(
    param: Annotated[GetJettonCPO, Query()],
    db_session: Session = Depends(get_db_session),
) -> list[JettonFDO]:
    jetton_service = JettonService(db_session)
    jettons = jetton_service.get_all(whitelisted_only=param.whitelisted_only)

    return [JettonFDO.from_orm(jetton) for jetton in jettons]


@admin_resource_router.get("/jettons/{jetton_address}")
async def get_jetton(
    jetton_address: str,
    db_session: Session = Depends(get_db_session),
) -> JettonFDO:
    jetton_service = JettonService(db_session)
    jetton_address_raw = userfriendly_to_raw(jetton_address)
    jetton = jetton_service.get(jetton_address_raw)

    return JettonFDO.from_orm(jetton)


@admin_resource_router.post("/jettons")
async def add_jetton(
    jetton: CreateJettonCPO,
    db_session: Session = Depends(get_db_session),
) -> JettonFDO:
    jetton_action = JettonAction(db_session)
    jetton_address_raw = userfriendly_to_raw(jetton.address)
    try:
        jetton = await jetton_action.create(address_raw=jetton_address_raw)
        return JettonFDO.model_validate(jetton.model_dump())
    except TONAPINotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Jetton not found",
        )


@admin_resource_router.put("/jettons/{jetton_address}")
async def update_jetton(
    jetton_address: str,
    jetton: UpdateJettonCPO,
    db_session: Session = Depends(get_db_session),
) -> JettonFDO:
    jetton_action = JettonAction(db_session)
    jetton_address_raw = userfriendly_to_raw(jetton_address)
    jetton = await jetton_action.update(
        address_raw=jetton_address_raw, is_enabled=jetton.is_enabled
    )
    return JettonFDO.model_validate(jetton.model_dump())


@admin_resource_router.get("/nft-collections")
async def get_nft_collections(
    param: Annotated[GetNftCollectionCPO, Query()],
    db_session: Session = Depends(get_db_session),
) -> list[NftCollectionFDO]:
    nft_collection_action = NftCollectionAction(db_session)
    return [
        NftCollectionFDO.model_validate(obj.model_dump())
        for obj in nft_collection_action.get_all(
            whitelisted_only=param.whitelisted_only
        )
    ]


@admin_resource_router.get("/nft-collections/{nft_collection_address}")
async def get_nft_collection(
    nft_collection_address: str,
    db_session: Session = Depends(get_db_session),
) -> NftCollectionFDO:
    nft_collection_action = NftCollectionAction(db_session)
    address_raw = userfriendly_to_raw(nft_collection_address)
    result = nft_collection_action.get(address_raw=address_raw)
    return NftCollectionFDO.model_validate(result.model_dump())


@admin_resource_router.post("/nft-collections")
async def add_nft_collection(
    nft_collection_data: CreateNftCollectionCPO,
    db_session: Session = Depends(get_db_session),
) -> NftCollectionFDO:
    nft_collection_action = NftCollectionAction(db_session)
    try:
        result = await nft_collection_action.create(
            address_raw=nft_collection_data.address
        )
        return NftCollectionFDO.model_validate(result.model_dump())
    except TONAPINotFoundError:
        raise HTTPException(
            status_code=404,
            detail="NFT collection not found",
        )


@admin_resource_router.put("/nft-collections/{nft_collection_address}")
async def update_nft_collection(
    nft_collection_address: str,
    nft_collection_data: UpdateNftCollectionCPO,
    db_session: Session = Depends(get_db_session),
) -> NftCollectionFDO:
    nft_collection_action = NftCollectionAction(db_session)
    address_raw = userfriendly_to_raw(nft_collection_address)
    result = await nft_collection_action.update(
        address_raw=address_raw, is_enabled=nft_collection_data.is_enabled
    )
    return NftCollectionFDO.model_validate(result.model_dump())


@admin_resource_router.post("/nft-collections/{nft_collection_address}/metadata")
async def refresh_nft_collection_metadata(
    nft_collection_address: str,
    db_session: Session = Depends(get_db_session),
) -> StatusFDO:
    nft_collection_action = NftCollectionAction(db_session)
    address_raw = userfriendly_to_raw(nft_collection_address)
    await nft_collection_action.refresh_metadata(address_raw)
    return StatusFDO(
        status="success",
        message="Metadata refresh initiated. It could take some time",
    )
