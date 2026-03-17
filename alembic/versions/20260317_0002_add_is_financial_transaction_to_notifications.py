from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260317_0002"
down_revision: str | None = "20260312_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "notifications",
        sa.Column("is_financial_transaction", sa.Boolean(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("notifications", "is_financial_transaction")
