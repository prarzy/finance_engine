"""multi_hop_and_postgresql

Revision ID: a1b2c3d4e5f6
Revises: 5a9165c30fb6
Create Date: 2026-05-19 11:00:00.000000

Changes:
- Converts tables from SQLite-compatible schema to PostgreSQL-native types.
- Adds hop_count, route_path (JSONB) to transactions.
- Adds hop_count, path (JSONB), breakdown (JSONB) to routes.
- Adds index on transactions.created_at.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers
revision = "a1b2c3d4e5f6"
down_revision = "5a9165c30fb6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── transactions: add multi-hop columns ──────────────────────────────────
    op.add_column(
        "transactions",
        sa.Column("hop_count", sa.Integer(), nullable=True, server_default="1"),
    )
    op.add_column(
        "transactions",
        sa.Column("route_path", JSONB(), nullable=True),
    )
    # Index on created_at for history queries
    op.create_index(
        "ix_transactions_created_at",
        "transactions",
        ["created_at"],
        unique=False,
    )

    # ── routes: add multi-hop columns ────────────────────────────────────────
    op.add_column(
        "routes",
        sa.Column("hop_count", sa.Integer(), nullable=True, server_default="1"),
    )
    op.add_column(
        "routes",
        sa.Column("path", JSONB(), nullable=True),
    )
    op.add_column(
        "routes",
        sa.Column("breakdown", JSONB(), nullable=True),
    )


def downgrade() -> None:
    # routes
    op.drop_column("routes", "breakdown")
    op.drop_column("routes", "path")
    op.drop_column("routes", "hop_count")

    # transactions
    op.drop_index("ix_transactions_created_at", table_name="transactions")
    op.drop_column("transactions", "route_path")
    op.drop_column("transactions", "hop_count")
