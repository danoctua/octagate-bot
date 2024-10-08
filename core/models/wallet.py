import datetime

from pytonapi.utils import to_amount
from sqlalchemy import ForeignKey, String, DateTime, Integer, Index
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import mapped_column, relationship

from core.db import Base
from core.settings import Config
from core.utils.number import human_friendly_number


class UserWallet(Base):
    __tablename__ = "user_wallet"

    user_id = mapped_column(ForeignKey("user.id"), primary_key=True)
    address = mapped_column(String(255), unique=True, nullable=False)
    created_at = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow
    )
    updated_at = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
    jetton_wallet_address = mapped_column(
        ForeignKey("jetton_wallet.owner_address"), nullable=True
    )
    jetton_wallet = relationship("JettonWallet", backref="user_wallet", lazy="joined")


class JettonWallet(Base):
    __tablename__ = "jetton_wallet"

    owner_address = mapped_column(String(255), primary_key=True)
    balance = mapped_column(BIGINT, default=0, nullable=False)
    rating = mapped_column(Integer, default=888888, nullable=False)
    created_at = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow
    )
    updated_at = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
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


class NftWallet(Base):
    __tablename__ = "nft_wallet"

    item_address = mapped_column(String(255), primary_key=True)
    owner_address = mapped_column(String(255), nullable=False, index=True)
    collection_address = mapped_column(String(255), nullable=False)
    created_at = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow
    )
    updated_at = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    __table_args__ = (
        Index(
            "nft_wallet_owner_address_collection_address",
            "owner_address",
            "collection_address",
        ),
    )
