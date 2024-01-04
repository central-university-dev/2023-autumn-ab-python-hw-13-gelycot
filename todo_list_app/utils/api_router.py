import inspect
import json
from datetime import datetime

import jwt
from pydantic import BaseModel

from todo_list_app.config import JWT_SECRET_KEY
from todo_list_app.utils.session_manager import session_manager


class ApiRouter:
    def __init__(self, prefix=''):
        self.routes = []
        self.prefix = prefix

    def post(self, path, private=False):
        def wrapper(funk):
            self.routes.append([self.prefix + path + 'POST', funk, private])
            return funk

        return wrapper

    def put(self, path, private=False):
        def wrapper(funk):
            self.routes.append([self.prefix + path + 'PUT', funk, private])
            return funk

        return wrapper

    def delete(self, path, private=False):
        def wrapper(funk):
            self.routes.append([self.prefix + path + 'DELETE', funk, private])
            return funk

        return wrapper

    def get(self, path_with_params: str, private=False):
        def wrapper(funk):
            if '|' in path_with_params:
                path = path_with_params[: path_with_params.index('|')]
            else:
                path = path_with_params
            self.routes.append([self.prefix + path + 'GET', funk, private])
            return funk

        return wrapper

    def check_api_route(self, scope, path, data):
        method = scope['method']
        body = ''

        for route_info in self.routes:
            route_path, funk, requires_authentication = route_info
            if path + method == route_path:
                if requires_authentication and not (
                    self._check_jwt_token(scope)
                    or self._check_session_token(scope)
                ):
                    body = {'error': 'Send correct token'}
                    break
                kwargs = self._parse_data_into_kwargs(data, funk, scope)
                body = funk(**kwargs)

        if isinstance(body, BaseModel):
            body = body.model_dump_json()
        if isinstance(body, dict):
            body = json.dumps(body)
        return body

    @staticmethod
    def _get_jwt_token(scope):
        token = None
        for head in scope['headers']:
            if b'authentication' in head:
                token = head[1].decode('UTF-8').split()[1]
        return token

    def _check_jwt_token(self, scope):
        token = self._get_jwt_token(scope)

        try:
            decoded_token = jwt.decode(
                token, JWT_SECRET_KEY, algorithms=['HS256']
            )

            current_time = datetime.utcnow()
            expiration_time = decoded_token.get('exp', 0)
            if current_time < datetime.utcfromtimestamp(expiration_time):
                scope['token_data'] = decoded_token
                return True
            else:
                return False

        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    @staticmethod
    def _check_session_token(scope):
        session_token = scope.get('session_token')
        user_id = session_manager.get_user_id(session_token)
        if user_id:
            return True
        return False

    @staticmethod
    def _parse_data_into_kwargs(data, funk, scope):
        for param in inspect.signature(funk).parameters.values():
            if param.name == 'scope':
                data['scope'] = scope
            elif param.name not in data:
                addition_kwarg = {}
                for param_name in inspect.signature(
                    param.annotation
                ).parameters.keys():
                    addition_kwarg[param_name] = data[param_name]
                    del data[param_name]

                data[param.name] = param.annotation(**addition_kwarg)
            else:
                data[param.name] = param.annotation(data[param.name])

        return data

    def include_routes(self, api_router: 'ApiRouter'):
        self.routes += api_router.routes
        return self


router = ApiRouter()
