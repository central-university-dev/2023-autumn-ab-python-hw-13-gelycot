"""add cascade deleting in foreign keys

Revision ID: 9a549ec5eeba
Revises: 72a945adcb07
Create Date: 2023-12-28 15:14:53.158534

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a549ec5eeba'
down_revision: Union[str, None] = '72a945adcb07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('task_list_id_fkey', 'task', type_='foreignkey')
    op.create_foreign_key(None, 'task', 'task_list', ['list_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('task_list_user_id_fkey', 'task_list', type_='foreignkey')
    op.create_foreign_key(None, 'task_list', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'task_list', type_='foreignkey')
    op.create_foreign_key('task_list_user_id_fkey', 'task_list', 'users', ['user_id'], ['id'])
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.create_foreign_key('task_list_id_fkey', 'task', 'task_list', ['list_id'], ['id'])
    # ### end Alembic commands ###
