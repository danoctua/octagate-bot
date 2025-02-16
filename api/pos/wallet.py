from api.pos.base import BaseFDO
from api.pos.ton import TonProofPO


class WalletDetailsWithProofPO(BaseFDO):
    ton_proof: TonProofPO
    wallet_address: str
    public_key: str
