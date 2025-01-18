from sqlalchemy import String, Boolean, DateTime, func, BigInteger
from sqlalchemy.dialects.mysql import TEXT
from sqlalchemy.orm import mapped_column

from core.db import Base


class Jetton(Base):
    __tablename__ = "jetton"

    address = mapped_column(String(255), primary_key=True)
    name = mapped_column(String(255), nullable=False)
    description = mapped_column(TEXT, nullable=True)
    symbol = mapped_column(String(255), nullable=False)
    total_supply = mapped_column(BigInteger, nullable=False)
    logo_path = mapped_column(String(290), nullable=True)
    is_enabled = mapped_column(Boolean, nullable=False, default=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())


class NFTCollection(Base):
    __tablename__ = "nft_collection"

    address = mapped_column(String(255), primary_key=True)
    name = mapped_column(String(255), nullable=False)
    description = mapped_column(TEXT, nullable=True)
    is_enabled = mapped_column(Boolean, nullable=False, default=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
