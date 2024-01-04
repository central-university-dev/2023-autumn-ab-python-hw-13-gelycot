from sqlalchemy import create_engine, Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

from todo_list_app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum('admin', 'user', name='user_roles'), default='user')
    salt = Column(String, nullable=False)


class TaskList(Base):
    __tablename__ = "task_list"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String, nullable=False)


class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True)
    list_id = Column(Integer, ForeignKey('task_list.id'))
    name = Column(String, nullable=False)


def get_session():
    session = Session()
    return session
