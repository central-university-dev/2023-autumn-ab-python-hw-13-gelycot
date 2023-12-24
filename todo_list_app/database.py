from sqlalchemy import create_engine, Column, Integer, String, Enum
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


def get_session():
    session = Session()
    return session



