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
            param_type = None
            for param in inspect.signature(funk).parameters.values():
                param_type = param.annotation
            self.routes.append([path + 'POST', funk, param_type, privat])
            return funk
        return wrapper

    def delete(self, path, privat=False):
        def wrapper(funk):
            param_type = None
            for param in inspect.signature(funk).parameters.values():
                param_type = param.annotation
            self.routes.append([path + 'DELETE', funk, param_type, privat])
            return funk
        return wrapper

    def get(self, path_with_params: str, privat=False):
        def wrapper(funk):
            param_types = []
            if '|' in path_with_params:
                path = path_with_params[:path_with_params.index('|')]
            else:
                path = path_with_params
            for param in inspect.signature(funk).parameters.values():
                param_type = param.annotation
                if param_type:
                    param_types.append(param_type)
            self.routes.append([path + 'GET', funk, param_types, privat])
            return funk

        return wrapper

    def check_api_route(self, scope, path, data):
        body = ''
        if scope['method'] == 'GET':
            for route_info in self.routes:
                if path + scope['method'] == route_info[0]:
                    if route_info[3] and not self._check_authentication(scope):
                        body = 'Send correct jwt token'
                        break
                    params = []
                    if data:
                        for param_type, param in zip(route_info[2], data.values()):
                            params.append(param_type(param))
                    body = route_info[1](*params)
        else:
            for route_info in self.routes:
                if path + scope['method'] == route_info[0]:
                    if route_info[3] and not self._check_authentication(scope):
                        body = 'Send correct jwt token'
                        break
                    if route_info[2] is None:
                        body = route_info[1]()
                    else:
                        body = route_info[1](route_info[2](**data))

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
                return True
            else:
                return False

        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    def include_routes(self, api_router: 'ApiRouter'):
        self.routes += api_router.routes


router = ApiRouter()