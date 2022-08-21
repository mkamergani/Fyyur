"""empty message

Revision ID: 77172df28bcb
Revises: 6579bdc87f07
Create Date: 2022-08-20 22:14:39.145825

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '77172df28bcb'
down_revision = '6579bdc87f07'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('artists', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.drop_column('artists', 'looking_for_venues')
    op.drop_column('artists', 'website_link')
    op.add_column('shows', sa.Column('start_time', sa.DateTime(), nullable=True))
    op.add_column('venues', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('venues', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.drop_column('venues', 'looking_for_talent')
    op.drop_column('venues', 'website_link')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('website_link', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('venues', sa.Column('looking_for_talent', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('venues', 'seeking_talent')
    op.drop_column('venues', 'website')
    op.drop_column('shows', 'start_time')
    op.add_column('artists', sa.Column('website_link', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('artists', sa.Column('looking_for_venues', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('artists', 'seeking_venue')
    op.drop_column('artists', 'website')
    # ### end Alembic commands ###
