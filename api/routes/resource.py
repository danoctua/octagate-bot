import logging

from fastapi import APIRouter, Depends, HTTPException

from api.deps import validate_access_token
from api.pos.ton import JettonFDO
from core.services.db import DBService
from core.services.jetton import JettonService
from core.services.user import UserService

logger = logging.getLogger(__name__)

resource_router = APIRouter(prefix="/resources")


@resource_router.get("/jettons")
async def get_jettons(
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
        jettons = jetton_service.get_all()

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
