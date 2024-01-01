from urllib.parse import parse_qs

from todo_list_app.api_router import ApiRouter
from todo_list_app.api_router import router
from todo_list_app.auth import router as auth_router
from todo_list_app.api import router as api_router
from todo_list_app.web import router as web_router


class App:

    def __init__(self, api_router: ApiRouter):
        self.api_router = api_router

    async def __call__(self, scope, receive, send):
        """
        Echo the method and path back in an HTTP response.
        """
        assert scope['type'] == 'http'
        self._parse_cookies(scope)
        if scope['method'] == 'GET':
            data = scope['query_string']
        else:
            data = await self.read_body(receive)

        if data:
            data = self.parse_body(data)
        else:
            data = {}
        path = scope['path']
        body = self.api_router.check_api_route(scope, path, data)
        headers = [(b'content-type', scope.get('content-type', 'application/json').encode('UTF-8'))]

        if 'Set-Cookie' in scope:
            for cookie in scope['Set-Cookie']:
                headers.append(('Set-Cookie'.encode('UTF-8'), cookie.encode('UTF-8')))

        await send({
            'type': 'http.response.start',
            'status': scope.get('status-code', 200),
            'headers': headers
        })
        await send({
            'type': 'http.response.body',
            'body': body.encode('UTF-8'),
        })

    @staticmethod
    async def read_body(receive):
        """
        Read and return the entire body from an incoming ASGI message.
        """
        body = b''
        more_body = True

        while more_body:
            message = await receive()
            body += message.get('body', b'')
            more_body = message.get('more_body', False)

        return body

    @staticmethod
    def parse_body(body):
        decoded_data = body.decode('UTF-8')
        parsed_data = parse_qs(decoded_data)

        body = {key: value[0] for key, value in parsed_data.items()}
        return body

    @staticmethod
    def _parse_cookies(scope):
        for head in scope['headers']:
            if b'cookie' in head:
                cookies = head[1].decode('UTF-8')
                cookie_pairs = cookies.split('; ')
                for cookie_pair in cookie_pairs:
                    key, value = cookie_pair.split('=')
                    scope[key] = value


app = App(api_router=router)
app.api_router.include_routes(auth_router).include_routes(api_router).include_routes(web_router)
