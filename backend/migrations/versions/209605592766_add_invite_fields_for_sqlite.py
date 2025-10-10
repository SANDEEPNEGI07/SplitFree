"""add invite fields for sqlite

Revision ID: 209605592766
Revises: b935078c58dc
Create Date: 2025-10-07 01:08:25.210291

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '209605592766'
down_revision = 'b935078c58dc'
branch_labels = None
depends_on = None


def upgrade():
    # Add the group_invitations table
    op.create_table('group_invitations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('invite_token', sa.String(length=36), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('used_at', sa.DateTime(), nullable=True),
    sa.Column('invited_by_user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.ForeignKeyConstraint(['invited_by_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('invite_token')
    )
    
    # Check if columns already exist, if not add them
    import sqlite3
    from sqlalchemy import text
    
    connection = op.get_bind()
    
    # Check if invite_code column exists
    result = connection.execute(text("PRAGMA table_info(groups)"))
    columns = [row[1] for row in result]
    
    # Add columns if they don't exist
    with op.batch_alter_table('groups', schema=None) as batch_op:
        if 'invite_code' not in columns:
            batch_op.add_column(sa.Column('invite_code', sa.String(length=20), nullable=True))
        if 'is_public' not in columns:
            batch_op.add_column(sa.Column('is_public', sa.Boolean(), nullable=True))
    
    # Generate invite codes for existing groups and set defaults
    import random
    import string
    
    # Get all existing groups
    result = connection.execute(text("SELECT id FROM groups WHERE invite_code IS NULL OR is_public IS NULL"))
    group_ids = [row[0] for row in result]
    
    # Generate unique invite codes for existing groups
    used_codes = set()
    for group_id in group_ids:
        # Generate unique invite code
        while True:
            letters = ''.join(random.choices(string.ascii_uppercase, k=3))
            numbers = ''.join(random.choices(string.digits, k=3))
            code = f"SPLIT-{letters}{numbers}"
            if code not in used_codes:
                used_codes.add(code)
                break
        
        # Update the group with invite code and set as public by default
        connection.execute(
            text("UPDATE groups SET invite_code = :code, is_public = 1 WHERE id = :id"),
            {"code": code, "id": group_id}
        )
    
    # Now make the columns NOT NULL and add unique constraint with explicit name
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.alter_column('invite_code', nullable=False)
        batch_op.alter_column('is_public', nullable=False)
        batch_op.create_unique_constraint('uq_groups_invite_code', ['invite_code'])


def downgrade():
    # Remove the constraints and columns
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.drop_constraint('uq_groups_invite_code', type_='unique')
        batch_op.drop_column('is_public')
        batch_op.drop_column('invite_code')
    
    # Drop the group_invitations table
    op.drop_table('group_invitations')
