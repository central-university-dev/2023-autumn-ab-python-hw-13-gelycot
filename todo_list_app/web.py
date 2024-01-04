from todo_list_app.utils.api_router import ApiRouter
from todo_list_app.auth import generate_csrf_token
from todo_list_app.config import env
from todo_list_app.crud import create_task_list_db
from todo_list_app.utils.session_manager import session_manager

router = ApiRouter(prefix='/web')


@router.get('/create-task-list', private=False)
def get_task_list_form(scope):
    scope['content-type'] = 'text/html'
    csrf_token = generate_csrf_token()
    task_list_form_template = env.get_template('task_list_form.html').render(
        csrf_token=csrf_token
    )
    scope['Set-Cookie'] = [f'csrf_token={csrf_token}']
    return task_list_form_template


@router.post('/create-task-list', private=False)
def check_task_list_form(name: str, csrf_token: str, scope):
    scope['content-type'] = 'text/html'
    if scope['csrf_token'] != csrf_token:
        return 'Wrong csrf_token'
    scope['Set-Cookie'] = ['csrf_token=delete; Max-Age=0']
    session_token = scope['session_token']
    user_id = session_manager.get_user_id(session_token)
    new_task_list = create_task_list_db(user_id, name)
    template = env.get_template('new_task_list.html')
    html_content = template.render(
        task_list_id=new_task_list.id, task_list_name=new_task_list.name
    )
    return html_content
