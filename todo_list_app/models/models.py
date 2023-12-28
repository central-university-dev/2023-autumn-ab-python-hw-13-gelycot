from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, Enum, ForeignKeyConstraint

metadata = MetaData()


users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String, unique=True),
    Column('password_hash', String, nullable=False),
    Column('role', Enum('admin', 'user', name='user_roles'), default='user'),
    Column('salt', String, nullable=False),
)

task_list = Table(
    'task_list',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer),
    Column('name', String, nullable=False),
    ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
)

task = Table(
    'task',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('list_id', Integer),
    Column('name', String, nullable=False),
    ForeignKeyConstraint(['list_id'], ['task_list.id'], ondelete='CASCADE')
)