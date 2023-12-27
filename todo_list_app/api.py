from todo_list_app.api_router import ApiRouter
from todo_list_app.contracts import CreateTaskList, CreateTask, UpdateTaskList
from todo_list_app.database import get_session, TaskList, Task

router = ApiRouter()


@router.post('/create-task-list', private=True)
def create_task_list(task_list: CreateTaskList, scope):
    token_data = scope['token_data']
    user_id = token_data['id']
    new_task = TaskList(user_id=user_id, name=task_list.name)
    with get_session() as session:
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        task_list_id = new_task.id
        task_list_name = new_task.name

    return {'task_list_id': task_list_id, 'task_list_name': task_list_name}


@router.post('/create-task', private=True)
def create_task(task: CreateTask, scope):
    token_data = scope['token_data']
    user_id = token_data['id']

    new_task = Task(list_id=task.list_id, name=task.name)
    with get_session() as session:
        task_list = session.query(TaskList).filter(TaskList.id == task.list_id).first()

        if task_list is None:
            return {'error': 'Task list not found.'}

        if task_list.user_id != user_id:
            return {'error': 'You do not have permission to create a task in this list.'}

        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        task_id = new_task.id
        task_name = new_task.name

    return {'task_id': task_id, 'task_name': task_name}


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

        task_list.name = updated_task_list.name
        session.commit()
        session.refresh(task_list)

        updated_task_list_name = task_list.name

    return {'updated_task_list_name': updated_task_list_name}
