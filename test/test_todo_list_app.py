import json

from test.test_client import TestClient
from todo_list_app.database import get_session, User
from todo_list_app.server import app
client = TestClient(app)


# def test_register_user():
#     data = {'username': 'test_user', 'password': 'password'}
#     response = client.post('/register', data=data)
#     assert type(response['id']) is int and response['username'] == 'test_user'
#     with get_session() as session:
#         user_to_delete = session.query(User).filter_by(username=response['username']).first()
#
#         session.delete(user_to_delete)
#         session.commit()


def test_auth():
    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/register', data=data)

    assert type(response['id']) is int and response['username'] == 'test_user'

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token_type = response['token_type']

    assert token_type == 'bearer'

    with get_session() as session:
        user_to_delete = session.query(User).filter_by(username='test_user').first()

        session.delete(user_to_delete)
        session.commit()
