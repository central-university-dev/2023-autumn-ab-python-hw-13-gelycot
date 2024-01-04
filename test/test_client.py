import json

from todo_list_app.utils.server import App


class TestClient:
    __test__ = False

    def __init__(self, app: App):
        self.app = app

    def request(self, path, data=None, scope=None):
        response = self.app.api_router.check_api_route(scope, path, data)

        if scope.get('content-type', 'application/json') == 'application/json':
            response = json.loads(response)
        return response

    def get(
        self,
        path,
        data: dict[str, str | int] = None,
        headers: dict[str, str] = None,
        scope_data: dict[str, str] = None,
    ):
        request_headers = []
        if headers is not None:
            for header, value in headers.items():
                request_headers.append(
                    (header.encode('utf-8'), value.encode('utf-8'))
                )
        scope = {
            'method': 'GET',
            'headers': request_headers,
            'path': path,
            'type': 'http',
        }
        if scope_data is not None:
            scope.update(scope_data)
        if data is None:
            data = {}

        return self.request(path, scope=scope, data=data)

    def post(
        self,
        path,
        data: dict[str, str | int] = None,
        headers: dict[str, str] = None,
        scope_data: dict[str, str] = None,
    ):
        request_headers = []
        if headers is not None:
            for header, value in headers.items():
                request_headers.append(
                    (header.encode('utf-8'), value.encode('utf-8'))
                )
        scope = {
            'method': 'POST',
            'headers': request_headers,
            'path': path,
            'type': 'http',
        }
        if scope_data is not None:
            scope.update(scope_data)
        if data is None:
            data = {}

        return self.request(path, scope=scope, data=data)

    def put(
        self,
        path,
        data: dict[str, str | int] = None,
        headers: dict[str, str] = None,
        scope_data: dict[str, str] = None,
    ):
        request_headers = []
        if headers is not None:
            for header, value in headers.items():
                request_headers.append(
                    (header.encode('utf-8'), value.encode('utf-8'))
                )
        scope = {
            'method': 'PUT',
            'headers': request_headers,
            'path': path,
            'type': 'http',
        }
        if scope_data is not None:
            scope.update(scope_data)
        if data is None:
            data = {}

        return self.request(path, scope=scope, data=data)

    def delete(
        self,
        path,
        data: dict[str, str | int] = None,
        headers: dict[str, str] = None,
        scope_data: dict[str, str] = None,
    ):
        request_headers = []
        if headers is not None:
            for header, value in headers.items():
                request_headers.append(
                    (header.encode('utf-8'), value.encode('utf-8'))
                )
        scope = {
            'method': 'DELETE',
            'headers': request_headers,
            'path': path,
            'type': 'http',
        }
        if scope_data is not None:
            scope.update(scope_data)
        if data is None:
            data = {}

        return self.request(path, scope=scope, data=data)
