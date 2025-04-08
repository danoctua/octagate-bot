from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.params import Query
from sqlalchemy.orm import Session
from starlette.requests import Request

from api.deps import get_db_session
from api.pos.user import UserFDO, UpdateUserWalletFDO
from api.pos.wallet import ConnectWalletRequestCPO, SetWalletRequestCPO
from core.actions.wallet import WalletAction
from core.exceptions.chat import TelegramChatNotExists
from core.exceptions.wallet import (
    UserWalletConnectedError,
    UserWalletConnectedAnotherUserError,
    ProofValidationError,
    UserWalletNotConnectedError,
)

user_router = APIRouter(prefix="/users")


@user_router.get("/me", tags=["User"])
async def get_user_data(
    request: Request,
) -> UserFDO:
    return UserFDO.from_orm(request.state.user)


@user_router.post(
    "/wallet",
    name="Connect user wallet to the chat with TON Proof",
    description="Connect a new wallet to the chat by providing TON proof and wallet details.",
    tags=["Wallet"],
)
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


@user_router.put(
    "/wallet",
    name="Set connected user wallet for the chat",
    description="Allows to set previously connected wallet for the chat.",
    tags=["Wallet"],
)
async def set_user_wallet(
    request: Request,
    request_data: SetWalletRequestCPO,
    db_session: Session = Depends(get_db_session),
) -> UpdateUserWalletFDO:
    wallet_action = WalletAction(db_session)
    try:
        await wallet_action.set_wallet(
            user_id=request.state.user.id,
            chat_slug=request_data.chat_slug,
            wallet_address=request_data.walletAddress,
        )
    except TelegramChatNotExists:
        raise HTTPException(
            detail={"error": {"message": "Chat not found"}},
            status_code=404,
        )
    except UserWalletNotConnectedError:
        raise HTTPException(
            detail={"error": {"message": "User has no connected wallet"}},
            status_code=400,
        )

    return UpdateUserWalletFDO(
        user=UserFDO.from_orm(request.state.user),
        # No need to refresh wallet details if it is already a tracked wallet
        task_id=None,
    )


@user_router.delete(
    "/wallet",
    name="Disconnect user wallet from the chat",
    description="Disconnect wallet from the chat.",
    tags=["Wallet"],
)
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
