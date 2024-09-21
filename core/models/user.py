import datetime

from sqlalchemy import Integer, String, DateTime, Boolean, BigInteger
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

    @property
    def full_name(self) -> str:
        return " ".join(filter(lambda x: x, [self.first_name, self.last_name]))
