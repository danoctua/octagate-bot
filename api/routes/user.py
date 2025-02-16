from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import NoResultFound

from api.deps import validate_access_token
from api.pos.user import UserFDO, UpdateUserWalletFDO
from api.pos.wallet import WalletDetailsWithProofPO
from core.actions.wallet import WalletAction
from core.services.db import DBService
from core.services.ton import TonProofService, ProofValidationError
from core.services.user import UserService
from core.services.wallet import UserWalletExistError, UserWalletConnectedError

user_router = APIRouter(prefix="/users")


@user_router.get("/me")
async def get_user_data(
    user_id: int = Depends(validate_access_token),
) -> UserFDO:
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        user = user_service.get(user_id=user_id)
        return UserFDO(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            is_premium=user.is_premium,
            language_code=user.language,
            photo_url=None,
            wallet_address=user.wallet.address if user.wallet else None,
        )


@user_router.post("/wallet")
async def update_wallet_address(
    wallet_details: WalletDetailsWithProofPO,
    user_id: int = Depends(validate_access_token),
) -> UpdateUserWalletFDO:
    try:
        TonProofService.verify_ton_proof(wallet_details=wallet_details)
    except ProofValidationError as e:
        raise HTTPException(
            detail={"error": {"message": str(e)}},
            status_code=400,
        )

    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        try:
            user = user_service.get(user_id=user_id)
        except NoResultFound:
            raise HTTPException(
                detail={"error": {"message": "User not found"}},
                status_code=404,
            )

        wallet_action = WalletAction(db_session)

        try:
            task_id = await wallet_action.connect_wallet(
                user_id=user.id, wallet_address=wallet_details.wallet_address
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

        return UpdateUserWalletFDO(
            user=UserFDO(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                is_premium=user.is_premium,
                language_code=user.language,
                photo_url=None,
                wallet_address=user.wallet.address,
            ),
            task_id=task_id,
        )


@user_router.delete("/wallet")
async def disconnect_wallet(
    user_id: int = Depends(validate_access_token),
) -> UserFDO:
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        try:
            user = user_service.get(user_id=user_id)
        except NoResultFound:
            raise HTTPException(
                detail={"error": {"message": "User not found"}},
                status_code=404,
            )

        wallet_action = WalletAction(db_session)
        await wallet_action.disconnect_wallet(telegram_id=user.telegram_id)

        return UserFDO(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            is_premium=user.is_premium,
            language_code=user.language,
            photo_url=None,
            wallet_address=None,
        )
