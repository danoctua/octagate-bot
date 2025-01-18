from pytonapi.utils import to_amount
from sqlalchemy import ForeignKey, String, DateTime, Integer, Index, Boolean, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import mapped_column

from core.constants import DEFAULT_WALLET_BALANCE
from core.db import Base
from core.settings import Config
from core.utils.number import human_friendly_number


class UserWallet(Base):
    __tablename__ = "user_wallet"

    address = mapped_column(String(255), primary_key=True)
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


class JettonWallet(Base):
    __tablename__ = "jetton_wallet"

    address = mapped_column(String(255), primary_key=True)
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
    def is_whale(self) -> bool:
        return (
            self.rating <= Config.WHALE_RATING_THRESHOLD
            and to_amount(self.balance) >= Config.WHALE_BALANCE_THRESHOLD
        )

    @property
    def balance_friendly(self) -> str:
        amount = to_amount(self.balance, precision=0)
        return human_friendly_number(amount)


class NftItem(Base):
    __tablename__ = "nft_item"

    address = mapped_column(String(255), primary_key=True)
    owner_address = mapped_column(String(255), nullable=False, index=True)
    collection_address = mapped_column(String(255), nullable=False)
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "nft_wallet_owner_address_collection_address",
            "owner_address",
            "collection_address",
        ),
    )
