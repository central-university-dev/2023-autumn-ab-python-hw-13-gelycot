from datetime import datetime, timedelta

import bcrypt
import jwt

from todo_list_app.config import JWT_SECRET_KEY
from todo_list_app.contracts import RegisterUser, RegisterUserResponse, LoginUser
from todo_list_app.database import User, get_session
from todo_list_app.api_router import ApiRouter

router = ApiRouter()


@router.post("/register", privat=False)
def register(user: RegisterUser):
    user_salt = bcrypt.gensalt()

    password_hash = bcrypt.hashpw(user.password.encode('UTF-8'), user_salt)
    new_user = User(username=user.username, password_hash=password_hash.decode('UTF-8'), salt=user_salt.decode('UTF-8'))
    with get_session() as session:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        new_user_id = new_user.id
        new_user_username = new_user.username

    return RegisterUserResponse(id=new_user_id, username=new_user_username)


@router.post("/token", privat=False)
def login_for_access_token(user: LoginUser):
    username = user.username
    provided_password = user.password
    with get_session() as session:
        db_user = session.query(User).filter(User.username == username).first()

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

