import inspect
import json
from datetime import datetime

import jwt
from pydantic import BaseModel

from todo_list_app.config import JWT_SECRET_KEY


class ApiRouter:

    def __init__(self):
        self.routes = []

    def post(self, path, privat=False):
        def wrapper(funk):
            self.routes.append([path + 'POST', funk, privat])
            return funk
        return wrapper

    def delete(self, path, privat=False):
        def wrapper(funk):
            self.routes.append([path + 'DELETE', funk, privat])
            return funk
        return wrapper

    def get(self, path_with_params: str, privat=False):
        def wrapper(funk):
            if '|' in path_with_params:
                path = path_with_params[:path_with_params.index('|')]
            else:
                path = path_with_params
            self.routes.append([path + 'GET', funk, privat])
            return funk

        return wrapper

    def check_api_route(self, scope, path, data):
        body = ''
        if scope['method'] == 'GET':
            for route_info in self.routes:
                if path + scope['method'] == route_info[0]:
                    funk = route_info[1]
                    if route_info[2] and not self._check_authentication(scope):
                        body = 'Send correct jwt token'
                        break
                    params = []
                    kwargs = {}
                    if data:
                        for param, param_value in zip(inspect.signature(funk).parameters.values(), data.values()):
                            if param.name != 'scope':
                                params.append(param.annotation(param_value))
                            else:
                                kwargs = {'scope': scope}
                    body = funk(*params, **kwargs)
        else:
            for route_info in self.routes:
                if path + scope['method'] == route_info[0]:
                    funk = route_info[1]
                    if route_info[2] and not self._check_authentication(scope):
                        body = 'Send correct jwt token'
                        break
                    kwargs = {}
                    for param in inspect.signature(funk).parameters.values():
                        if param.name != 'scope':
                            kwargs[f'{param.name}'] = param.annotation(**data)
                        else:
                            kwargs['scope'] = scope
                    body = funk(**kwargs)

        if isinstance(body, BaseModel):
            body = body.model_dump_json()
        if isinstance(body, dict):
            body = json.dumps(body)
        return body

    @staticmethod
    def _check_authentication(scope):
        token = ''
        for head in scope['headers']:
            if b'authentication' in head:
                token = head[1].decode('UTF-8').split()[1]
        try:
            decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])

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

    def include_routes(self, api_router: 'ApiRouter'):
        self.routes += api_router.routes
        return self


router = ApiRouter()