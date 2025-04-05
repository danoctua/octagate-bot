from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.params import Query
from sqlalchemy.orm import Session
from starlette.requests import Request

from api.deps import get_db_session
from api.pos.user import UserFDO, UpdateUserWalletFDO
from api.pos.wallet import ConnectWalletRequestCPO
from core.actions.wallet import WalletAction
from core.exceptions.chat import TelegramChatNotExists
from core.exceptions.wallet import (
    UserWalletConnectedError,
    UserWalletConnectedAnotherUserError,
    ProofValidationError,
)

user_router = APIRouter(prefix="/users")


@user_router.get("/me")
async def get_user_data(
    request: Request,
) -> UserFDO:
    return UserFDO.from_orm(request.state.user)


@user_router.post("/wallet")
async def connect_user_wallet(
    request: Request,
    request_data: ConnectWalletRequestCPO,
    db_session: Session = Depends(get_db_session),
) -> UpdateUserWalletFDO:
    wallet_action = WalletAction(db_session)

    try:
        task_id = await wallet_action.connect_wallet(
            user_id=request.state.user.id,
            chat_slug=request_data.chat_slug,
            wallet_details=request_data.wallet_details,
        )
    except UserWalletConnectedError:
        raise HTTPException(
            detail={
                "error": {"message": "Wallet already connected to another account"}
            },
            status_code=400,
        )
    except UserWalletConnectedAnotherUserError:
        raise HTTPException(
            detail={"error": {"message": "User already has a connected wallet"}},
            status_code=400,
        )
    except TelegramChatNotExists:
        raise HTTPException(
            detail={"error": {"message": "Chat not found"}},
            status_code=404,
        )
    except ProofValidationError as e:
        raise HTTPException(
            detail={"error": {"message": str(e)}},
            status_code=400,
        )

    return UpdateUserWalletFDO(
        user=UserFDO.from_orm(request.state.user),
        task_id=task_id,
    )


@user_router.delete("/wallet")
async def disconnect_wallet(
    request: Request,
    chat_slug: Annotated[
        str,
        Query(
            ...,
            alias="chatSlug",
            description="Chat slug for which wallet will be disconnected",
        ),
    ],
    db_session: Session = Depends(get_db_session),
) -> UserFDO:
    wallet_action = WalletAction(db_session)
    await wallet_action.disconnect_wallet(
        user_id=request.state.user.id, chat_slug=chat_slug
    )
    return UserFDO.from_orm(request.state.user)
