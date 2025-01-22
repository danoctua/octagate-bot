"""migrate initial data

Revision ID: 3285a761c4fd
Revises: e4acf6e9d41f
Create Date: 2025-01-21 14:15:06.057960

"""
from typing import Sequence, Union

from alembic import op

from core.settings import core_settings

# revision identifiers, used by Alembic.
revision: str = "3285a761c4fd"
down_revision: Union[str, None] = "e4acf6e9d41f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


BANNED_PUBLIC_WALLETS = [
    "0:779dcc815138d9500e449c5291e7f12738c23d575b5310000f6a253bd607384e",  # stonfi router
    "0:0000000000000000000000000000000000000000000000000000000000000000",  # burn address
]


def upgrade() -> None:
    op.execute(
        f"""
            INSERT INTO {core_settings.mysql_database}.user (id, telegram_id, is_premium, username, first_name, last_name, language, is_blocked, is_admin, created_at)
            SELECT id, telegram_id, is_premium, username, first_name, last_name, language, is_blocked, 0, created_at
            FROM anon.user
        """
    )

    # Migrate data from anon.user_wallet to {CURRENT_SCHEMA}.user_wallet
    op.execute(
        f"""
            INSERT INTO {core_settings.mysql_database}.user_wallet (address, user_id, created_at, updated_at, hide_wallet)
            SELECT address, user_id, created_at, updated_at, hide_wallet
            FROM anon.user_wallet
        """
    )

    pass


def downgrade() -> None:
    op.execute(f"DELETE FROM {core_settings.mysql_database}.user")
    op.execute(f"DELETE FROM {core_settings.mysql_database}.user_wallet")
