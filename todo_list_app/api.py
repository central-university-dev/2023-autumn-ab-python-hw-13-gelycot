from todo_list_app.api_router import ApiRouter
from todo_list_app.contracts import CreateTaskList, CreateTask, UpdateTaskList
from todo_list_app.crud import create_task_list_db, get_task_list_by_id_db, create_task_db, update_task_list_db, \
    get_tasks_by_list_id_db
from todo_list_app.database import get_session, TaskList, Task

router = ApiRouter()


@router.get('/task_list|task_list_id', private=True)
def get_task_list(task_list_id: int, scope):
    token_data = scope['token_data']
    user_id = token_data['id']
    user_role = token_data['role']

    task_list = get_task_list_by_id_db(task_list_id)

    if task_list is None:
        return {'error': 'Task list not found.'}

    tasks = get_tasks_by_list_id_db(task_list.id)
    if user_role == 'admin':
        return {'user_id': task_list.user_id, 'list_id': task_list.id, 'list_name': task_list.name, 'task_ids': tasks}
    else:
        if task_list.user_id == user_id:
            return {'user_id': task_list.user_id, 'list_id': task_list.id, 'list_name': task_list.name, 'task_ids': tasks}
        else:
            return {'error': 'You do not have permission to access this task list.'}


@router.post('/create-task-list', private=True)
def create_task_list(task_list: CreateTaskList, scope):
    token_data = scope['token_data']
    user_id = token_data['id']
    new_task_list = create_task_list_db(user_id, task_list.name)

    return {'task_list_id': new_task_list.id, 'task_list_name': new_task_list.name}


@router.post('/create-task', private=True)
def create_task(task: CreateTask, scope):
    token_data = scope['token_data']
    user_id = token_data['id']

    with get_session() as session:
        task_list = session.query(TaskList).filter(TaskList.id == task.list_id).first()

        if task_list is None:
            return {'error': 'Task list not found.'}

        if task_list.user_id != user_id:
            return {'error': 'You do not have permission to create a task in this list.'}

    new_task = create_task_db(task.list_id, task.name)

    return {'task_id': new_task.id, 'task_name': new_task.name}


@router.put('/update-task-list', private=True)
def update_task_list(updated_task_list: UpdateTaskList, scope):
    token_data = scope['token_data']
    user_id = token_data['id']

    with get_session() as session:
        task_list = session.query(TaskList).filter(TaskList.id == updated_task_list.list_id).first()

        if task_list is None:
            return {'error': 'Task list not found.'}

        if task_list.user_id != user_id:
            return {'error': 'You do not have permission to update this task list.'}

    updated_task_list = update_task_list_db(updated_task_list.list_id, updated_task_list.name)

    return {'updated_task_list_name': updated_task_list.name}
