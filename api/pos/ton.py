from pydantic import BaseModel


class TonProofDomainPO(BaseModel):
    length_bytes: int
    value: str

    class Config:
        extra = "ignore"


class TonProofPO(BaseModel):
    timestamp: int
    domain: TonProofDomainPO
    signature: str
    payload: str
