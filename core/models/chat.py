import datetime

from sqlalchemy import (
    BigInteger,
    String,
    DateTime,
    func,
    Boolean,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import mapped_column, relationship, Mapped

from core.db import Base
from core.dtos.base import NftItemAttributeDTO
from core.models.fields import TelegramChatNftCollectionMetadataField


class TelegramChat(Base):
    __tablename__ = "telegram_chat"

    id = mapped_column(BigInteger, primary_key=True)
    username = mapped_column(String(255), nullable=True)
    title = mapped_column(String(255), nullable=False)
    description = mapped_column(String(255), nullable=True)
    slug = mapped_column(String(255), nullable=False, unique=True)
    is_forum = mapped_column(Boolean, nullable=False, default=False)
    logo_path = mapped_column(String(55), nullable=True)
    invite_link = mapped_column(
        String(255),
        nullable=True,
        doc="Invite link to the chat. If empty, the chat will not be accessible.",
    )
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    whitelist_external_sources = relationship(
        "TelegramChatWhitelistExternalSource",
        backref="chat",
        cascade="all, delete-orphan",
    )
    whitelist_sources = relationship(
        "TelegramChatWhitelist",
        backref="chat",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<TelegramChat(id={self.id}, title={self.title})>"


class TelegramChatRuleBase(Base):
    __abstract__ = True

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id = mapped_column(
        ForeignKey("telegram_chat.id", ondelete="CASCADE"), nullable=False
    )
    threshold = mapped_column(
        BigInteger, nullable=False, doc="Minimum amount of items to hold"
    )
    grants_write_access = mapped_column(Boolean, nullable=False, default=False)
    is_enabled = mapped_column(Boolean, nullable=False, default=True)
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class TelegramChatJetton(TelegramChatRuleBase):
    __tablename__ = "telegram_chat_jetton"

    address = mapped_column(
        ForeignKey("jetton.address", ondelete="CASCADE"), nullable=False
    )
    jetton = relationship(
        "Jetton",
        back_populates="telegram_chat_jettons",
        lazy="joined",
    )

    def __repr__(self):
        return f"<TelegramChatJetton({self.address=}, {self.chat_id=})>"


class TelegramChatNFTCollection(TelegramChatRuleBase):
    __tablename__ = "telegram_chat_nft_collection"

    address = mapped_column(
        ForeignKey("nft_collection.address", ondelete="CASCADE"), nullable=False
    )
    required_attributes: Mapped[list[NftItemAttributeDTO]] = mapped_column(
        TelegramChatNftCollectionMetadataField,
        nullable=True,
        doc="List of required attributes to hold, e.g. `[{'rarity': 'legendary'}, {'type': 'weapon'}]`",
    )

    nft_collection = relationship(
        "NFTCollection",
        back_populates="telegram_chat_nft_collections",
        lazy="joined",
    )

    def __repr__(self):
        return f"<TelegramChatNFTCollection({self.address=}, {self.chat_id=})>"


class TelegramChatWhitelistBase(Base):
    __abstract__ = True

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id = mapped_column(
        ForeignKey("telegram_chat.id", ondelete="CASCADE"), nullable=False
    )
    name = mapped_column(String(255), nullable=False)
    description = mapped_column(String(255), nullable=True)
    is_enabled = mapped_column(Boolean, nullable=False, default=True)
    content = mapped_column(
        JSON,
        nullable=True,
        doc="List of Telegram IDs as integers that are allowed to access the chat, e.g. `[123455, 122234, 123456]`",
    )
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=datetime.datetime.now,
        nullable=False,
    )


class TelegramChatWhitelistExternalSource(TelegramChatWhitelistBase):
    __tablename__ = "telegram_chat_whitelist_external_source"

    url = mapped_column(String(255), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "chat_id", "name", name="uix_chat_external_source_chat_name_unique"
        ),
    )

    def __repr__(self):
        return f"<TelegramChatWhitelistExternalSource({self.url=}, {self.chat_id=})>"


class TelegramChatWhitelist(TelegramChatWhitelistBase):
    __tablename__ = "telegram_chat_whitelist"

    def __repr__(self):
        return f"<TelegramChatWhitelist({self.chat_id=}, {self.name=})>"

    __table_args__ = (
        UniqueConstraint("chat_id", "name", name="uix_chat_whitelist_chat_name_unique"),
    )


class TelegramChatUser(Base):
    __tablename__ = "telegram_chat_user"

    user_id = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    chat_id = mapped_column(
        ForeignKey("telegram_chat.id", ondelete="CASCADE"), primary_key=True
    )
    is_admin = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Whether the user is an admin in the chat",
    )
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User", lazy="joined")
    chat = relationship("TelegramChat", lazy="joined")

    def __repr__(self):
        return f"<TelegramChatUser(user_id={self.user_id}, chat_id={self.chat_id})>"
