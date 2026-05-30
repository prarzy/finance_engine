"""Add constraint tables: currencies, providers, provider_corridors, compliance_rules, and kyc_tier to users

Revision ID: b1c2d3e4f5a6
Revises: a1b2c3d4e5f6
Create Date: 2026-05-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'b1c2d3e4f5a6'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Create currencies table
    op.create_table('currencies',
        sa.Column('code', sa.String(3), nullable=False),
        sa.Column('name', sa.String(64), nullable=False),
        sa.Column('symbol', sa.String(8), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('can_hold', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_source_only', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('code')
    )

    # Create providers table
    op.create_table('providers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('slug', sa.String(32), nullable=False),
        sa.Column('display_name', sa.String(64), nullable=False),
        sa.Column('fx_spread_pct', sa.Numeric(6, 4), nullable=False),
        sa.Column('fixed_fee_usd', sa.Numeric(10, 4), nullable=False),
        sa.Column('variable_fee_pct', sa.Numeric(6, 4), nullable=False),
        sa.Column('settlement_hours', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )

    # Create provider_corridors table
    op.create_table('provider_corridors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('provider_slug', sa.String(32), nullable=False),
        sa.Column('source_currency', sa.String(3), nullable=False),
        sa.Column('target_currency', sa.String(3), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('max_transfer_usd', sa.Numeric(14, 2), nullable=True),
        sa.Column('min_transfer_usd', sa.Numeric(10, 2), nullable=False, server_default='1.00'),
        sa.Column('kyc_tier_required', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['provider_slug'], ['providers.slug']),
        sa.ForeignKeyConstraint(['source_currency'], ['currencies.code']),
        sa.ForeignKeyConstraint(['target_currency'], ['currencies.code']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider_slug', 'source_currency', 'target_currency', name='unique_corridor')
    )
    
    # Create indexes for provider_corridors
    op.create_index('idx_corridors_provider', 'provider_corridors', ['provider_slug'])
    op.create_index('idx_corridors_source', 'provider_corridors', ['source_currency'])
    op.create_index('idx_corridors_target', 'provider_corridors', ['target_currency'])
    op.create_index('idx_corridors_active', 'provider_corridors', ['is_active'],
                    postgresql_where=sa.text("is_active = true"))

    # Create compliance_rules table
    op.create_table('compliance_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('rule_type', sa.String(32), nullable=False),
        sa.Column('provider_slug', sa.String(32), nullable=True),
        sa.Column('currency_code', sa.String(3), nullable=True),
        sa.Column('rule_value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('source_citation', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['provider_slug'], ['providers.slug']),
        sa.ForeignKeyConstraint(['currency_code'], ['currencies.code']),
        sa.PrimaryKeyConstraint('id')
    )

    # Add kyc_tier column to users table
    op.add_column('users', sa.Column('kyc_tier', sa.Integer(), nullable=False, server_default='1'))

    # Add constraint_snapshot column to transactions table
    op.add_column('transactions', sa.Column('constraint_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade():
    # Remove constraint_snapshot from transactions
    op.drop_column('transactions', 'constraint_snapshot')

    # Remove kyc_tier from users
    op.drop_column('users', 'kyc_tier')

    # Drop compliance_rules table
    op.drop_table('compliance_rules')

    # Drop indexes for provider_corridors
    op.drop_index('idx_corridors_active', table_name='provider_corridors')
    op.drop_index('idx_corridors_target', table_name='provider_corridors')
    op.drop_index('idx_corridors_source', table_name='provider_corridors')
    op.drop_index('idx_corridors_provider', table_name='provider_corridors')

    # Drop provider_corridors table
    op.drop_table('provider_corridors')

    # Drop providers table
    op.drop_table('providers')

    # Drop currencies table
    op.drop_table('currencies')
