from sqlalchemy import update

from test.test_client import TestClient
from todo_list_app.auth import generate_csrf_token
from todo_list_app.database import get_session, User
from todo_list_app.asgi import app

client = TestClient(app)


def create_temporary_user(username='test_user') -> dict:
    data = {'username': username, 'password': 'password'}
    response = client.post('/register', data=data)
    return response


def assign_admin_role(username):
    with get_session() as session:
        user = session.query(User).filter_by(username=username).first()
        session.execute(
            update(User).where(User.id == user.id).values(role='admin')
        )
        session.commit()


def delete_temporary_user(username):
    with get_session() as session:
        user_to_delete = (
            session.query(User).filter_by(username=username).first()
        )

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
    response = client.post(
        '/api/create-task-list', data=task_list_data, headers=headers
    )
    assert response['task_list_name'] == 'New Task List' and isinstance(
        response['task_list_id'], int
    )
    delete_temporary_user(username='test_user')


def test_should_get_task_list():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post(
        '/api/create-task-list', data=task_list_data, headers=headers
    )

    task_list_id = response['task_list_id']
    headers = {'authentication': f'Bearer {token}'}
    data = {'task_list_id': task_list_id}
    response = client.get('/api/task_list', headers=headers, data=data)
    assert response['list_name'] == 'New Task List'
    delete_temporary_user(username='test_user')


def test_should_get_task_list_by_admin():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post(
        '/api/create-task-list', data=task_list_data, headers=headers
    )
    task_list_id = response['task_list_id']

    create_temporary_user('test_admin')
    data = {'username': 'test_admin', 'password': 'password'}
    response = client.post('/token', data=data)
    admin_token = response['access_token']

    headers = {'authentication': f'Bearer {admin_token}'}
    data = {'task_list_id': task_list_id}
    response = client.get('/api/task_list', headers=headers, data=data)
    assert (
        response['error']
        == 'You do not have permission to access this task list.'
    )

    assign_admin_role('test_admin')
    data = {'username': 'test_admin', 'password': 'password'}
    response = client.post('/token', data=data)
    admin_token = response['access_token']

    headers = {'authentication': f'Bearer {admin_token}'}
    data = {'task_list_id': task_list_id}
    response = client.get('/api/task_list', headers=headers, data=data)
    assert response['list_name'] == 'New Task List'
    delete_temporary_user(username='test_user')
    delete_temporary_user(username='test_admin')


def test_should_not_get_nonexistent_task_list():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    headers = {'authentication': f'Bearer {token}'}
    data = {'task_list_id': 0}
    response = client.get('/api/task_list', headers=headers, data=data)
    assert response['error'] == 'Task list not found.'
    delete_temporary_user(username='test_user')


def test_send_wrong_jwt():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token'] + 'wrong'

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post(
        '/api/create-task-list', data=task_list_data, headers=headers
    )

    assert response['error'] == 'Send correct token'
    delete_temporary_user(username='test_user')


def test_should_update_task_list():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post(
        '/api/create-task-list', data=task_list_data, headers=headers
    )
    list_id = response['task_list_id']

    task_list_data = {'name': 'New Task List Name', 'list_id': list_id}
    headers = {'authentication': f'Bearer {token}'}
    response = client.put(
        '/api/update-task-list', data=task_list_data, headers=headers
    )
    assert response['updated_task_list_name'] == 'New Task List Name'
    delete_temporary_user(username='test_user')


def test_should_not_update_nonexistent_task_list():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List Name', 'list_id': 0}
    headers = {'authentication': f'Bearer {token}'}
    response = client.put(
        '/api/update-task-list', data=task_list_data, headers=headers
    )
    assert response['error'] == 'Task list not found.'
    delete_temporary_user(username='test_user')


def test_should_not_update_task_list_without_permission():
    create_temporary_user('test_user1')
    create_temporary_user('test_user2')

    data = {'username': 'test_user1', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post(
        '/api/create-task-list', data=task_list_data, headers=headers
    )
    list_id = response['task_list_id']

    data = {'username': 'test_user2', 'password': 'password'}
    response = client.post('/token', data=data)
    token_user2 = response['access_token']

    task_list_data = {'name': 'New Task List Name', 'list_id': list_id}
    headers = {'authentication': f'Bearer {token_user2}'}
    response = client.put(
        '/api/update-task-list', data=task_list_data, headers=headers
    )
    assert (
        response['error']
        == 'You do not have permission to update this task list.'
    )
    delete_temporary_user(username='test_user1')
    delete_temporary_user(username='test_user2')


def test_should_delete_task_list():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post(
        '/api/create-task-list', data=task_list_data, headers=headers
    )
    list_id = response['task_list_id']

    data = {'list_id': list_id}
    headers = {'authentication': f'Bearer {token}'}
    response = client.delete(
        '/api/delete-task-list', data=data, headers=headers
    )
    assert (
        response['message']
        == 'Task list "New Task List" deleted successfully.'
    )
    delete_temporary_user('test_user')


def test_should_not_delete_nonexistent_task_list():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    data = {'list_id': 0}
    headers = {'authentication': f'Bearer {token}'}
    response = client.delete(
        '/api/delete-task-list', data=data, headers=headers
    )
    assert response['error'] == 'Task list not found.'
    delete_temporary_user('test_user')


def test_should_not_delete_task_list_without_permission():
    create_temporary_user('test_user1')
    create_temporary_user('test_user2')

    data = {'username': 'test_user1', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post(
        '/api/create-task-list', data=task_list_data, headers=headers
    )
    list_id = response['task_list_id']

    data = {'username': 'test_user2', 'password': 'password'}
    response = client.post('/token', data=data)
    token_user2 = response['access_token']

    task_list_data = {'list_id': list_id}
    headers = {'authentication': f'Bearer {token_user2}'}
    response = client.delete(
        '/api/delete-task-list', data=task_list_data, headers=headers
    )
    assert (
        response['error']
        == 'You do not have permission to delete this task list.'
    )
    delete_temporary_user(username='test_user1')
    delete_temporary_user(username='test_user2')


def test_should_create_task():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post(
        '/api/create-task-list', data=task_list_data, headers=headers
    )
    list_id = response['task_list_id']

    task_data = {'name': 'New Task', 'list_id': list_id}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post('/api/create-task', headers=headers, data=task_data)
    assert response['task_name'] == 'New Task', isinstance(
        response['task_id'], int
    )
    delete_temporary_user(username='test_user')


def test_should_not_create_task_to_nonexistent_task_list():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_data = {'name': 'New Task', 'list_id': 0}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post('/api/create-task', headers=headers, data=task_data)
    assert response['error'] == 'Task list not found.'
    delete_temporary_user(username='test_user')


def test_should_not_not_create_task_without_permission():
    create_temporary_user('test_user1')
    create_temporary_user('test_user2')

    data = {'username': 'test_user1', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post(
        '/api/create-task-list', data=task_list_data, headers=headers
    )
    list_id = response['task_list_id']

    data = {'username': 'test_user2', 'password': 'password'}
    response = client.post('/token', data=data)
    token_user2 = response['access_token']

    task_data = {'name': 'New Task', 'list_id': list_id}
    headers = {'authentication': f'Bearer {token_user2}'}
    response = client.post('/api/create-task', headers=headers, data=task_data)
    assert (
        response['error']
        == 'You do not have permission to create a task in this list.'
    )
    delete_temporary_user(username='test_user1')
    delete_temporary_user(username='test_user2')


def test_should_get_task():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post(
        '/api/create-task-list', data=task_list_data, headers=headers
    )

    task_list_id = response['task_list_id']
    task_data = {'name': 'New Task', 'list_id': task_list_id}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post('/api/create-task', headers=headers, data=task_data)
    task_id = response['task_id']

    task_data = {'task_id': task_id}
    headers = {'authentication': f'Bearer {token}'}
    response = client.get('/api/task', headers=headers, data=task_data)
    assert response['task_name'] == 'New Task', (
        response['list_id'] == task_list_id
    )
    delete_temporary_user(username='test_user')


def test_should_get_task_by_admin():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post(
        '/api/create-task-list', data=task_list_data, headers=headers
    )
    task_list_id = response['task_list_id']

    task_data = {'name': 'New Task', 'list_id': task_list_id}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post('/api/create-task', headers=headers, data=task_data)
    task_id = response['task_id']

    create_temporary_user('test_admin')
    data = {'username': 'test_admin', 'password': 'password'}
    response = client.post('/token', data=data)
    admin_token = response['access_token']

    headers = {'authentication': f'Bearer {admin_token}'}
    data = {'task_id': task_id}
    response = client.get('/api/task', headers=headers, data=data)
    assert (
        response['error'] == 'You do not have permission to access this task.'
    )

    assign_admin_role('test_admin')
    data = {'username': 'test_admin', 'password': 'password'}
    response = client.post('/token', data=data)
    admin_token = response['access_token']

    headers = {'authentication': f'Bearer {admin_token}'}
    data = {'task_id': task_id}
    response = client.get('/api/task', headers=headers, data=data)
    assert response['task_name'] == 'New Task', (
        response['list_id'] == task_list_id
    )
    delete_temporary_user(username='test_user')
    delete_temporary_user(username='test_admin')


def test_should_not_get_nonexistent_task():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    headers = {'authentication': f'Bearer {token}'}
    data = {'task_id': 0}
    response = client.get('/api/task', headers=headers, data=data)
    assert response['error'] == 'Task not found.'
    delete_temporary_user(username='test_user')


def test_should_update_task():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post(
        '/api/create-task-list', data=task_list_data, headers=headers
    )

    task_list_id = response['task_list_id']
    task_data = {'name': 'New Task', 'list_id': task_list_id}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post('/api/create-task', headers=headers, data=task_data)
    task_id = response['task_id']

    task_data = {'name': 'New Task Name', 'task_id': task_id}
    headers = {'authentication': f'Bearer {token}'}
    response = client.put('/api/update-task', data=task_data, headers=headers)
    assert response['updated_task_name'] == 'New Task Name'
    delete_temporary_user(username='test_user')


def test_should_not_update_nonexistent_task():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_data = {'name': 'New Task Name', 'task_id': 0}
    headers = {'authentication': f'Bearer {token}'}
    response = client.put('/api/update-task', data=task_data, headers=headers)
    assert response['error'] == 'Task not found.'
    delete_temporary_user(username='test_user')


def test_should_not_update_task_without_permission():
    create_temporary_user('test_user1')
    create_temporary_user('test_user2')

    data = {'username': 'test_user1', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post(
        '/api/create-task-list', data=task_list_data, headers=headers
    )

    task_list_id = response['task_list_id']
    task_data = {'name': 'New Task', 'list_id': task_list_id}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post('/api/create-task', headers=headers, data=task_data)
    task_id = response['task_id']

    data = {'username': 'test_user2', 'password': 'password'}
    response = client.post('/token', data=data)
    token_user2 = response['access_token']

    task_list_data = {'name': 'New Task Name', 'task_id': task_id}
    headers = {'authentication': f'Bearer {token_user2}'}
    response = client.put(
        '/api/update-task', data=task_list_data, headers=headers
    )
    assert (
        response['error'] == 'You do not have permission to update this task.'
    )
    delete_temporary_user(username='test_user1')
    delete_temporary_user(username='test_user2')


def test_should_delete_task():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post(
        '/api/create-task-list', data=task_list_data, headers=headers
    )

    task_list_id = response['task_list_id']
    task_data = {'name': 'New Task', 'list_id': task_list_id}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post('/api/create-task', headers=headers, data=task_data)
    task_id = response['task_id']

    data = {'task_id': task_id}
    headers = {'authentication': f'Bearer {token}'}
    response = client.delete('/api/delete-task', data=data, headers=headers)
    assert response['message'] == 'Task "New Task" deleted successfully.'
    delete_temporary_user('test_user')


def test_should_not_delete_nonexistent_task():
    create_temporary_user()

    data = {'username': 'test_user', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    data = {'task_id': 0}
    headers = {'authentication': f'Bearer {token}'}
    response = client.delete('/api/delete-task', data=data, headers=headers)
    assert response['error'] == 'Task not found.'
    delete_temporary_user('test_user')


def test_should_not_delete_task_without_permission():
    create_temporary_user('test_user1')
    create_temporary_user('test_user2')

    data = {'username': 'test_user1', 'password': 'password'}
    response = client.post('/token', data=data)
    token = response['access_token']

    task_list_data = {'name': 'New Task List'}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post(
        '/api/create-task-list', data=task_list_data, headers=headers
    )

    task_list_id = response['task_list_id']
    task_data = {'name': 'New Task', 'list_id': task_list_id}
    headers = {'authentication': f'Bearer {token}'}
    response = client.post('/api/create-task', headers=headers, data=task_data)
    task_id = response['task_id']

    data = {'username': 'test_user2', 'password': 'password'}
    response = client.post('/token', data=data)
    token_user2 = response['access_token']

    task_data = {'task_id': task_id}
    headers = {'authentication': f'Bearer {token_user2}'}
    response = client.delete(
        '/api/delete-task', data=task_data, headers=headers
    )
    assert (
        response['error'] == 'You do not have permission to delete this task.'
    )
    delete_temporary_user(username='test_user1')
    delete_temporary_user(username='test_user2')


def test_generate_csrf_token():
    csrf_token = generate_csrf_token()
    assert isinstance(csrf_token, str) and len(csrf_token) == 22
