
from test.test_client import TestClient
from todo_list_app.database import get_session, User
from todo_list_app.server import app

client = TestClient(app)


def create_temporary_user() -> dict:
    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/register', data=data)
    return response


def delete_temporary_user(username):
    with get_session() as session:
        user_to_delete = session.query(User).filter_by(username=username).first()

        session.delete(user_to_delete)
        session.commit()


def test_auth():
    response = create_temporary_user()
    username = response['username']

    assert type(response['id']) is int and response['username'] == 'test_user'

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token_type = response['token_type']

    assert token_type == 'bearer'
    delete_temporary_user(username)


def test_create_task_list():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post('/create-task-list', data=task_list_data, headers=headers)
    assert response['task_list_name'] == 'New Task List' and type(response['task_list_id']) == int
    delete_temporary_user(username='test_user')