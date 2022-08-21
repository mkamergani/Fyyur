"""empty message

Revision ID: 6579bdc87f07
Revises: c021f86ce0c8
Create Date: 2022-08-20 21:23:06.476161

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6579bdc87f07'
down_revision = 'c021f86ce0c8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shows',
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['venues.id'], ),
    sa.PrimaryKeyConstraint('venue_id', 'artist_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('shows')
    # ### end Alembic commands ###
