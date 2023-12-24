"""rename user table to "users"

Revision ID: 72a945adcb07
Revises: 964cf31dcc93
Create Date: 2023-12-24 15:42:12.024619

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '72a945adcb07'
down_revision: Union[str, None] = '964cf31dcc93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('role', sa.Enum('admin', 'user', name='user_roles'), nullable=True),
    sa.Column('salt', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.drop_table('user', cascade='all')
    op.drop_constraint('task_list_user_id_fkey', 'task_list', type_='foreignkey')
    op.create_foreign_key(None, 'task_list', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'task_list', type_='foreignkey')
    op.create_foreign_key('task_list_user_id_fkey', 'task_list', 'user', ['user_id'], ['id'])
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('password_hash', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('role', postgresql.ENUM('admin', 'user', name='user_roles'), autoincrement=False, nullable=True),
    sa.Column('salt', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='user_pkey'),
    sa.UniqueConstraint('username', name='user_username_key')
    )
    op.drop_table('users')
    # ### end Alembic commands ###
