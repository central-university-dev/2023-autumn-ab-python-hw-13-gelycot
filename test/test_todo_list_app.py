
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


def test_should_auth():
    response = create_temporary_user()
    username = response['username']

    assert type(response['id']) is int and response['username'] == 'test_user'

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token_type = response['token_type']

    assert token_type == 'bearer'
    delete_temporary_user(username)


def test_should_not_auth_nonexistent_user():

    data = {'username': 'nonexistent_user', 'password': 'password'}
    response = client.post('/token', data=data)
    assert response['detail'] == 'There is no nonexistent_user user'


def test_should_not_auth_wrong_password():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'wrong_password'}
    response = client.post('/token', data=data)
    assert response['detail'] == 'Unauthorized'
    delete_temporary_user('test_user')


def test_should_create_task_list():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post('/api/create-task-list', data=task_list_data, headers=headers)
    assert response['task_list_name'] == 'New Task List' and type(response['task_list_id']) == int
    delete_temporary_user(username='test_user')


def test_should_get_task_list():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post('/api/create-task-list', data=task_list_data, headers=headers)

    task_list_id = response['task_list_id']
    headers = {'authentication': f'Bearer {token}'}
    data = {'task_list_id': task_list_id}
    response = client.get('/api/task_list', headers=headers, data=data)
    assert response['list_name'] == 'New Task List'
    delete_temporary_user(username='test_user')


def test_send_wrong_jwt():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token'] + 'wrong'

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post('/api/create-task-list', data=task_list_data, headers=headers)

    assert response['error'] == 'Send correct jwt token'
    delete_temporary_user(username='test_user')