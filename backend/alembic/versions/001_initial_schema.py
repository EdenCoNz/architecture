"""Initial schema with users table

Revision ID: 001
Revises:
Create Date: 2025-10-18 22:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create initial database schema.

    Creates:
    - users table with authentication and profile fields
    - Indexes for common query patterns
    """
    # Create users table
    op.create_table(
        'users',
        # Primary key and timestamps (from BaseModel)
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),

        # Authentication fields
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),

        # Profile information
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),

        # Account status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),

        # Security tracking
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),

        # Primary key constraint
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users'))
    )

    # Create indexes
    # Single column indexes
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_is_active'), 'users', ['is_active'], unique=False)
    op.create_index(op.f('ix_users_is_superuser'), 'users', ['is_superuser'], unique=False)

    # Composite indexes for common query patterns
    op.create_index('ix_users_email_active', 'users', ['email', 'is_active'], unique=False)
    op.create_index('ix_users_superuser_active', 'users', ['is_superuser', 'is_active'], unique=False)


def downgrade() -> None:
    """
    Drop initial database schema.

    Drops:
    - All indexes on users table
    - users table
    """
    # Drop composite indexes
    op.drop_index('ix_users_superuser_active', table_name='users')
    op.drop_index('ix_users_email_active', table_name='users')

    # Drop single column indexes
    op.drop_index(op.f('ix_users_is_superuser'), table_name='users')
    op.drop_index(op.f('ix_users_is_active'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')

    # Drop table
    op.drop_table('users')
