from pytonapi.utils import to_amount
from sqlalchemy import ForeignKey, DateTime, Integer, Boolean, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import mapped_column

from core.constants import DEFAULT_WALLET_BALANCE
from core.db import Base
from core.models.fields import BLOCKCHAIN_ADDRESS_RAW
from core.utils.number import human_friendly_number


class UserWallet(Base):
    __tablename__ = "user_wallet"

    address = mapped_column(BLOCKCHAIN_ADDRESS_RAW, primary_key=True)
    user_id = mapped_column(ForeignKey("user.id"), unique=True, nullable=False)
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    hide_wallet = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<UserWallet(address={self.address}, user_id={self.user_id})>"


class JettonWallet(Base):
    __tablename__ = "jetton_wallet"

    address = mapped_column(BLOCKCHAIN_ADDRESS_RAW, primary_key=True)
    jetton_master_address = mapped_column(
        ForeignKey("jetton.address", ondelete="CASCADE"),
        nullable=False,
    )
    owner_address = mapped_column(
        ForeignKey("user_wallet.address", ondelete="CASCADE"),
        nullable=False,
    )
    balance = mapped_column(BIGINT, default=DEFAULT_WALLET_BALANCE, nullable=False)
    rating = mapped_column(Integer, default=None, nullable=True)
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @property
    def balance_friendly(self) -> str:
        amount = to_amount(self.balance, precision=0)
        return human_friendly_number(amount)

    def __repr__(self):
        return f"<JettonWallet(address={self.address}, jetton_master_address={self.jetton_master_address})>"
