import datetime

from pytonapi.utils import to_amount
from sqlalchemy import ForeignKey, String, DateTime, Integer, Index, Boolean
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import mapped_column, relationship

from core.constants import DEFAULT_WALLET_RATING, DEFAULT_WALLET_BALANCE
from core.db import Base
from core.settings import Config
from core.utils.number import human_friendly_number


class UserWallet(Base):
    __tablename__ = "user_wallet"

    user_id = mapped_column(ForeignKey("user.id"), primary_key=True)
    address = mapped_column(String(255), unique=True, nullable=False)
    created_at = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC)
    )
    updated_at = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.now(datetime.UTC),
        onupdate=datetime.datetime.now(datetime.UTC),
    )
    jetton_wallet_address = mapped_column(
        ForeignKey("jetton_wallet.owner_address"),
        nullable=True,
    )
    hide_wallet = mapped_column(Boolean, default=False, nullable=False)
    jetton_wallet = relationship("JettonWallet", backref="user_wallet", lazy="joined")


class JettonWallet(Base):
    __tablename__ = "jetton_wallet"

    owner_address = mapped_column(String(255), primary_key=True)
    balance = mapped_column(BIGINT, default=DEFAULT_WALLET_BALANCE, nullable=False)
    rating = mapped_column(Integer, default=DEFAULT_WALLET_RATING, nullable=False)
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
    def is_eligible_to_join_club(self) -> bool:
        return to_amount(self.balance) >= Config.CLUB_BALANCE_THRESHOLD

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
