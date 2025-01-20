import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from core.settings import Config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


# Database setup
DATABASE_URL = Config.DB_CONNECTION_STRING
engine = create_engine(DATABASE_URL, pool_size=300)
Base = declarative_base()
