from todo_list_app.api_router import ApiRouter
from todo_list_app.contracts import CreateTaskList, CreateTask
from todo_list_app.database import get_session, TaskList, Task

router = ApiRouter()


@router.post('/create-task-list', privat=True)
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


@router.post('/create-task', privat=True)
def create_task(task: CreateTask):
    new_task = Task(list_id=task.list_id, name=task.name)
    with get_session() as session:
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        task_id = new_task.id
        task_name = new_task.name

    return {'task_id': task_id, 'task_name': task_name}
