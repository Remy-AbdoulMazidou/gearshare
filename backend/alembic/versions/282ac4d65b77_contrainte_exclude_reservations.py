"""contrainte exclude reservations

Revision ID: 282ac4d65b77
Revises: 7f3fbd8a28c3
Create Date: 2026-10-30 22:38:01.783727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '282ac4d65b77'
down_revision: Union[str, None] = '7f3fbd8a28c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute(
        """
        ALTER TABLE reservations
        ADD CONSTRAINT reservations_active_no_overlap
        EXCLUDE USING gist (
            item_id WITH =,
            daterange(date_debut, date_fin, '[)') WITH &&
        ) WHERE (statut = 'active')
        """
    )


def downgrade() -> None:
    op.drop_constraint("reservations_active_no_overlap", "reservations")
    op.execute("DROP EXTENSION IF EXISTS btree_gist")