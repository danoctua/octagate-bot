from typing import Annotated

from pydantic import Field

from api.pos.base import BaseFDO
from core.dtos.wallet import WalletDetailsWithProofDTO


class WalletDetailsWithProofCPO(BaseFDO, WalletDetailsWithProofDTO):
    ...


class ConnectWalletRequestCPO(BaseFDO):
    chat_slug: Annotated[
        str,
        Field(
            ...,
            alias="chatSlug",
            description="Chat slug for which wallet is being connected",
        ),
    ]
    wallet_details: WalletDetailsWithProofCPO
