import secrets
from datetime import datetime, timedelta

import bcrypt
import jwt

from todo_list_app.config import JWT_SECRET_KEY, env
from todo_list_app.contracts import RegisterUser, RegisterUserResponse, LoginUser
from todo_list_app.crud import create_user_db
from todo_list_app.database import User, get_session
from todo_list_app.api_router import ApiRouter
from todo_list_app.session_manager import session_manager

router = ApiRouter()

session_tokens_manager = session_manager


def generate_csrf_token():
    return secrets.token_urlsafe(16)


@router.post("/register", private=False)
def register(user: RegisterUser):
    user_salt = bcrypt.gensalt()

    password_hash = bcrypt.hashpw(user.password.encode('UTF-8'), user_salt)
    new_user = create_user_db(user.username, password_hash.decode('UTF-8'), user_salt.decode('UTF-8'))

    return RegisterUserResponse(id=new_user.id, username=new_user.username)


@router.post("/token", private=False)
def login_for_access_token(user: LoginUser):
    username = user.username
    provided_password = user.password
    with get_session() as session:
        db_user = session.query(User).filter(User.username == username).first()
    if db_user is None:
        return {'detail': f'There is no {username} user'}
    if bcrypt.checkpw(provided_password.encode('UTF-8'), db_user.password_hash.encode('UTF-8')):
        expiration_time = datetime.utcnow() + timedelta(minutes=10)
        token_payload = {
            'id': db_user.id,
            'role': db_user.role,
            'exp': expiration_time
        }
        jwt_token = jwt.encode(token_payload, JWT_SECRET_KEY, algorithm='HS256')
        return {'access_token': jwt_token, 'token_type': 'bearer'}
    else:
        return {'detail': 'Unauthorized'}


@router.get('/login', private=False)
def send_login_form(scope):
    scope['content-type'] = 'text/html'
    csrf_token = generate_csrf_token()
    login_template = env.get_template('login_form.html').render(csrf_token=csrf_token)
    scope['Set-Cookie'] = [f'csrf_token={csrf_token}']
    return login_template


@router.post('/login', private=False)
def check_login_form_data(username: str, password: str, csrf_token: str, scope):
    if scope['csrf_token'] != csrf_token:
        return 'Wrong csrf_token'

    username = username
    provided_password = password

    with get_session() as session:
        db_user = session.query(User).filter(User.username == username).first()

    if db_user is None:
        return f'There is no {username} user'

    if bcrypt.checkpw(provided_password.encode('UTF-8'), db_user.password_hash.encode('UTF-8')):
        session_token = session_manager.create_session(db_user.id)
        scope['Set-Cookie'] = [f'session_token={session_token}']
        return f'Correct password. Welcome {username}'
    return 'Wrong password'


@router.get('/logout')
def logout_user(scope):
    session_token = scope.get('session_token')
    if session_token:
        session_manager.delete_session(session_token)
        scope['Set-Cookie'] = [f'session_token=deleted; Max-Age=0']
        return 'You arу logged out'
    return 'You did not log in'

