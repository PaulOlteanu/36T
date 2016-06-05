"""Create photo table

Revision ID: 05eab60b5613
Revises: None
Create Date: 2016-06-05 01:15:27.823835

"""

# revision identifiers, used by Alembic.
revision = '05eab60b5613'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('photo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=True),
        sa.Column('path', sa.String(length=128), nullable=True),
        sa.Column('votes', sa.Integer(), nullable=True),
        sa.Column('created_on', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('photo')
