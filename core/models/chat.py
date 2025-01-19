from sqlalchemy import BigInteger, String, DateTime, func, Boolean, ForeignKey
from sqlalchemy.orm import mapped_column

from core.db import Base


class TelegramChat(Base):
    __tablename__ = "telegram_chat"

    id = mapped_column(BigInteger, primary_key=True)
    username = mapped_column(String(255), nullable=True)
    title = mapped_column(String(255), nullable=False)
    is_forum = mapped_column(Boolean, nullable=False, default=False)
    logo_path = mapped_column(String(55), nullable=True)
    invite_link = mapped_column(
        String(255),
        nullable=True,
        doc="Invite link to the chat. If empty, the chat will not be accessible.",
    )
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<TelegramChat(id={self.id}, title={self.title})>"


class TelegramChatJetton(Base):
    __tablename__ = "telegram_chat_jetton"

    jetton_address = mapped_column(
        ForeignKey("jetton.address", ondelete="CASCADE"), primary_key=True
    )
    chat_id = mapped_column(
        ForeignKey("telegram_chat.id", ondelete="CASCADE"), primary_key=True
    )
    threshold = mapped_column(
        BigInteger, nullable=False, doc="Minimum amount of jettons to hold in nano"
    )
    whale_threshold = mapped_column(
        BigInteger,
        nullable=True,
        doc="Minimum amount of jettons to hold in nano to be considered a whale",
    )
    whale_label_template = mapped_column(
        String(25),
        nullable=True,
        doc="Label to be assigned to the user if they are a whale",
    )
    is_enabled = mapped_column(Boolean, nullable=False, default=True)
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class TelegramChatNFTCollection(Base):
    __tablename__ = "telegram_chat_nft_collection"

    collection_address = mapped_column(
        ForeignKey("nft_collection.address", ondelete="CASCADE"), primary_key=True
    )
    chat_id = mapped_column(
        ForeignKey("telegram_chat.id", ondelete="CASCADE"), primary_key=True
    )
    is_enabled = mapped_column(Boolean, nullable=False, default=True)
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# class TelegramChatExternalSource(Base):
#     TODO add external source support (e.g. get list of IDs to allow to join the chat)
#     __tablename__ = "telegram_chat_external_source"
#
#     chat_id = mapped_column(ForeignKey("telegram_chat.id"), primary_key=True)
#     is_enabled = mapped_column(Boolean, nullable=False, default=True)
#     created_at = mapped_column(
#         DateTime(timezone=True), server_default=func.now(), nullable=False
#     )


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
    is_whale_admin = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Whether the user is an admin in the chat that was promoted as a whale from the bot",
    )
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self):
        return f"<TelegramChatUser(user_id={self.user_id}, chat_id={self.chat_id})>"
