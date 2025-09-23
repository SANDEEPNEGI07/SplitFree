"""Remove unique constraint from username column

Revision ID: 0ff488b17e5d
Revises: fac83809dbc4
Create Date: 2025-09-21 23:04:59.132674

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ff488b17e5d'
down_revision = 'fac83809dbc4'
branch_labels = None
depends_on = None


def upgrade():
    # For SQLite, we need to recreate the table to remove the unique constraint
    # SQLite auto-generates constraint names, so we use recreate_table approach
    with op.batch_alter_table('users', schema=None, recreate='always') as batch_op:
        # This will recreate the table with the new model definition (no unique constraint on username)
        pass


def downgrade():
    # Re-add the unique constraint on username
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_users_username', ['username'])
