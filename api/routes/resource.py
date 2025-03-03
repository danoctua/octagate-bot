import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query

from api.deps import validate_access_token
from api.pos.ton import JettonFDO, CreateJettonCPO, UpdateJettonCPO, GetJettonCPO
from core.actions.jetton import JettonAction
from core.services.db import DBService
from core.services.jetton import JettonService
from core.services.user import UserService

logger = logging.getLogger(__name__)

resource_router = APIRouter(prefix="/resources")


@resource_router.get("/jettons")
async def get_jettons(
    param: Annotated[GetJettonCPO, Query()],
    user_id: int = Depends(validate_access_token),
) -> list[JettonFDO]:
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        requestor = user_service.get(user_id)
        if not requestor.is_admin:
            raise HTTPException(
                detail={
                    "error": {"message": "You are not allowed to access this resource"}
                },
                status_code=403,
            )

        jetton_service = JettonService(db_session)
        jettons = jetton_service.get_all(whitelisted_only=param.whitelisted_only)

        return [
            JettonFDO(
                address=jetton.address,
                name=jetton.name,
                description=jetton.description,
                symbol=jetton.symbol,
                logo_path=jetton.logo_path,
                is_enabled=jetton.is_enabled,
            )
            for jetton in jettons
        ]


@resource_router.get("/jettons/{jetton_address}")
async def get_jetton(
    jetton_address: str,
    user_id: int = Depends(validate_access_token),
) -> JettonFDO:
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        requestor = user_service.get(user_id)
        if not requestor.is_admin:
            raise HTTPException(
                detail={
                    "error": {"message": "You are not allowed to access this resource"}
                },
                status_code=403,
            )

        jetton_service = JettonService(db_session)
        jetton = jetton_service.get(jetton_address)

        return JettonFDO(
            address=jetton.address,
            name=jetton.name,
            description=jetton.description,
            symbol=jetton.symbol,
            logo_path=jetton.logo_path,
            is_enabled=jetton.is_enabled,
        )


@resource_router.post("/jettons")
async def add_jetton(
    jetton: CreateJettonCPO,
    user_id: int = Depends(validate_access_token),
) -> JettonFDO:
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        requestor = user_service.get(user_id)
        if not requestor.is_admin:
            raise HTTPException(
                detail={
                    "error": {"message": "You are not allowed to access this resource"}
                },
                status_code=403,
            )

        jetton_action = JettonAction(db_session)
        jetton = await jetton_action.create(jetton_address=jetton.address)
        return jetton


@resource_router.put("/jettons/{jetton_address}")
async def update_jetton(
    jetton_address: str,
    jetton: UpdateJettonCPO,
    user_id: int = Depends(validate_access_token),
) -> JettonFDO:
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        requestor = user_service.get(user_id)
        if not requestor.is_admin:
            raise HTTPException(
                detail={
                    "error": {"message": "You are not allowed to access this resource"}
                },
                status_code=403,
            )

        jetton_action = JettonAction(db_session)
        jetton = await jetton_action.update(
            jetton_address=jetton_address, is_enabled=jetton.is_enabled
        )
        return jetton
