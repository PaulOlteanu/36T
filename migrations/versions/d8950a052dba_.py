"""Create photo table

Revision ID: d8950a052dba
Revises: None
Create Date: 2016-06-05 12:52:42.367589

"""

# revision identifiers, used by Alembic.
revision = 'd8950a052dba'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('photo',
    sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=True),
        sa.Column('path', sa.String(length=128), nullable=True),
        sa.Column('votes', sa.Integer(), nullable=False),
        sa.Column('created_on', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('path')
    )


def downgrade():
    op.drop_table('photo')
