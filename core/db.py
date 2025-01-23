import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from core.settings import core_settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


# Database setup
DATABASE_URL = core_settings.db_connection_string
engine = create_engine(DATABASE_URL, pool_size=300)
Base = declarative_base()
