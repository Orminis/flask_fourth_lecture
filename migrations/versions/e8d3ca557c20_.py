"""empty message

Revision ID: e8d3ca557c20
Revises: c525c5c58afe
Create Date: 2022-07-23 17:08:39.962944

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.

revision = 'e8d3ca557c20'
down_revision = 'c525c5c58afe'
branch_labels = None
depends_on = None


def upgrade():
    role = postgresql.ENUM('user', 'admin', 'super_admin', name='userrole')
    role.create(op.get_bind())

    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('role', sa.Enum('user', 'admin', 'super_admin', name='userrole'), server_default='user', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'role')
    # ### end Alembic commands ###