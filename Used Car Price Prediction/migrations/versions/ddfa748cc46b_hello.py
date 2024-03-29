"""hello

Revision ID: ddfa748cc46b
Revises: c1e623a3652a
Create Date: 2023-05-21 16:55:31.725348

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ddfa748cc46b'
down_revision = 'c1e623a3652a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Users', sa.Column('kms_driven', sa.Float(), nullable=True))
    op.add_column('Users', sa.Column('present_price', sa.Float(), nullable=True))
    op.add_column('Users', sa.Column('year', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Users', 'year')
    op.drop_column('Users', 'present_price')
    op.drop_column('Users', 'kms_driven')
    # ### end Alembic commands ###
