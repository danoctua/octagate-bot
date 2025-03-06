from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request

from api.deps import get_db_session
from api.pos.user import UserFDO, UpdateUserWalletFDO
from api.pos.wallet import WalletDetailsWithProofPO
from core.actions.wallet import WalletAction
from core.services.ton import ProofValidationError
from core.services.wallet import UserWalletExistError, UserWalletConnectedError

user_router = APIRouter(prefix="/users")


@user_router.get("/me")
async def get_user_data(
    request: Request,
) -> UserFDO:
    return UserFDO.from_orm(request.state.user)


@user_router.post("/wallet")
async def update_wallet_address(
    request: Request,
    wallet_details: WalletDetailsWithProofPO,
    db_session: Session = Depends(get_db_session),
) -> UpdateUserWalletFDO:
    wallet_action = WalletAction(db_session)

    try:
        task_id = await wallet_action.connect_wallet(
            user_id=request.state.user.id, wallet_details=wallet_details
        )
    except UserWalletExistError:
        raise HTTPException(
            detail={
                "error": {"message": "Wallet already connected to another account"}
            },
            status_code=400,
        )
    except UserWalletConnectedError:
        raise HTTPException(
            detail={"error": {"message": "User already has a connected wallet"}},
            status_code=400,
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
    db_session: Session = Depends(get_db_session),
) -> UserFDO:
    wallet_action = WalletAction(db_session)
    await wallet_action.disconnect_wallet(telegram_id=request.state.user.telegram_id)
    return UserFDO.from_orm(request.state.user)
