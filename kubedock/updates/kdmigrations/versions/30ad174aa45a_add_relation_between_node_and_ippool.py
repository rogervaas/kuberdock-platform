"""Add relation between Node and IPPool

Revision ID: 3dc83a81f385
Revises: 30ad174aa45a
Create Date: 2016-06-07 09:40:05.047326

"""

# revision identifiers, used by Alembic.
revision = '3dc83a81f385'
down_revision = '3c832810a33c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ippool', sa.Column('node_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'ippool', 'nodes', ['node_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'ippool', type_='foreignkey')
    op.drop_column('ippool', 'node_id')
    ### end Alembic commands ###
