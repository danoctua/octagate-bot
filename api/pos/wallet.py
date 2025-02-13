from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from api.pos.ton import TonProofPO


class WalletDetailsWithProofPO(BaseModel):
    ton_proof: TonProofPO
    wallet_address: str
    public_key: str

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
