import datetime

from sqlalchemy import Integer, String, DateTime, Boolean, BigInteger, ForeignKey
from sqlalchemy.orm import mapped_column, relationship

from core.db import Base
from core.settings import Config


class User(Base):
    __tablename__ = "user"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id = mapped_column(BigInteger, unique=True, index=True)
    is_premium = mapped_column(Boolean, default=False, nullable=False)
    username = mapped_column(String(255), index=True, nullable=True)
    first_name = mapped_column(String(255), nullable=False)
    last_name = mapped_column(String(255), nullable=True)
    language = mapped_column(
        String(10), nullable=False, default=Config.DEFAULT_LANGUAGE
    )
    is_blocked = mapped_column(Boolean, nullable=False, default=False)

    created_at = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow
    )

    wallet = relationship(
        "UserWallet",
        uselist=False,
        backref="user",
        lazy="joined",
        primaryjoin="User.id == UserWallet.user_id",
    )
    chat_user = relationship(
        "ChatUser",
        uselist=False,
        backref="user",
        lazy="joined",
        primaryjoin="User.id == ChatUser.user_id",
    )

    @property
    def full_name(self) -> str:
        return " ".join(filter(lambda x: x, [self.first_name, self.last_name]))

    def is_eligible_club_member(self, is_nft_holder: bool) -> bool:
        return is_nft_holder or (
            self.wallet
            and self.wallet.jetton_wallet
            and self.wallet.jetton_wallet.is_whale
        )


class ChatUser(Base):
    __tablename__ = "chat_user"

    user_id = mapped_column(ForeignKey("user.id"), primary_key=True)
    invite_link = mapped_column(String(255), nullable=False)
    invite_link_expiry = mapped_column(DateTime(timezone=True), nullable=False)
    invite_link_activated = mapped_column(Boolean, default=False, nullable=False)
    created_at = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow
    )

    @property
    def is_invite_link_expired(self) -> bool:
        return (
            self.invite_link_activated
            or self.invite_link_expiry < datetime.datetime.utcnow()
        )
