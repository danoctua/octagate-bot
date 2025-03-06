import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.params import Query
from pytonapi.utils import userfriendly_to_raw
from sqlalchemy.orm import Session

from api.deps import get_db_session
from api.pos.ton import JettonFDO, CreateJettonCPO, UpdateJettonCPO, GetJettonCPO
from core.actions.jetton import JettonAction
from core.services.jetton import JettonService

logger = logging.getLogger(__name__)

admin_resource_router = APIRouter(prefix="/resources")


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
    jetton = await jetton_action.create(jetton_address=jetton.address)
    return jetton


@admin_resource_router.put("/jettons/{jetton_address}")
async def update_jetton(
    jetton_address: str,
    jetton: UpdateJettonCPO,
    db_session: Session = Depends(get_db_session),
) -> JettonFDO:
    jetton_action = JettonAction(db_session)
    jetton_address_raw = userfriendly_to_raw(jetton_address)
    jetton = await jetton_action.update(
        jetton_address=jetton_address_raw, is_enabled=jetton.is_enabled
    )
    return jetton
