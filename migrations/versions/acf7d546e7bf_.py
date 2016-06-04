"""empty message

Revision ID: acf7d546e7bf
Revises: None
Create Date: 2016-05-31 09:34:49.276890

"""

# revision identifiers, used by Alembic.
revision = 'acf7d546e7bf'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('photo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=True),
        sa.Column('path', sa.String(length=128), nullable=True),
        sa.Column('votes', sa.Integer(), nullable=True),
        sa.Column('created_on', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('photo')
