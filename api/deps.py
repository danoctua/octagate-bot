import hashlib
import hmac
import json
from typing import Annotated
from urllib.parse import unquote_plus

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.pos.auth import InitDataPO
from api.pos.user import UserInitDataPO
from api.services.authentication import AuthenticationService, UnauthorizedError
from api.settings import api_settings

security = HTTPBearer()


def validate_user_init_data(init_data_po: InitDataPO) -> UserInitDataPO:
    c_str = "WebAppData"

    init_data = init_data_po.init_data

    init_data = dict(
        sorted(
            [chunk.split("=") for chunk in init_data.split("&")],
            key=lambda x: x[0],
        )
    )

    _hash = init_data.pop("hash")

    # URL-decode the values
    init_data = {key: unquote_plus(value) for key, value in init_data.items()}

    # Generate the data_check_string
    data_check_string = "\n".join(
        [f"{key}={value}" for key, value in init_data.items()]
    )

    secret_key = hmac.new(
        c_str.encode(), api_settings.telegram_bot_token.encode(), hashlib.sha256
    ).digest()
    data_check = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256)

    if data_check.hexdigest() != _hash:
        raise HTTPException(status_code=400, detail="Invalid user data: wrong hash")

    user_data = json.loads(init_data.get("user", "{}"))
    user_data.pop("allows_write_to_pm", None)

    return UserInitDataPO(**user_data)


def validate_access_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> int:
    access_token = credentials.credentials
    try:
        user_id = AuthenticationService.verify_token(access_token)
        return user_id
    except UnauthorizedError:
        raise HTTPException(status_code=401, detail="Invalid access token")
