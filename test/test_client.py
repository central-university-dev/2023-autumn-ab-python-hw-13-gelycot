import json

from todo_list_app.server import App


class TestClient:

    def __init__(self, app: App):
        self.app = app

    def request(self, path, data=None, scope=None):
        return json.loads(self.app.api_router.check_api_route(scope, path, data))

    def get(self, path, data: dict[str, str | int] = None, headers: dict[str, str] = None):
        request_headers = []
        if headers is not None:
            for header, value in headers.items():
                request_headers.append((header.encode('utf-8'), value.encode('utf-8')))
        scope = {
            'method': 'GET',
            'headers': request_headers,
            'path': path,
            'type': 'http',
        }
        if data is None:
            data = {}

        return self.request(path, scope=scope, data=data)

    def post(self, path, data: dict[str, str | int] = None,  headers: dict[str, str] = None):
        request_headers = []
        if headers is not None:
            for header, value in headers.items():
                request_headers.append((header.encode('utf-8'), value.encode('utf-8')))
        scope = {'method': 'POST', 'headers': request_headers, 'path': path, 'type': 'http'}
        if data is None:
            data = {}

        return self.request(path, scope=scope, data=data)



