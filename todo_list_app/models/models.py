from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, Enum

metadata = MetaData()


user = Table(
    'user',
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
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('name', String, nullable=False),
)


task = Table(
    'task',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('list_id', Integer, ForeignKey('task_list.id')),
    Column('name', String, nullable=False),
)