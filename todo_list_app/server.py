from urllib.parse import unquote

from todo_list_app.api_router import ApiRouter
from todo_list_app.api_router import router
from todo_list_app.auth import router as auth_router
from todo_list_app.api import router as api_router


class App:

    def __init__(self, api_router: ApiRouter):
        self.api_router = api_router

    async def __call__(self, scope, receive, send):
        """
        Echo the method and path back in an HTTP response.
        """
        assert scope['type'] == 'http'
        if scope['method'] == 'GET':
            data = scope['query_string']
            if data:
                data = self.parse_body(data)
        else:
            data = await self.read_body(receive)
        path = scope['path']
        body = self.api_router.check_api_route(scope, path, data)

        await send({
            'type': 'http.response.start',
            'status': 200 if body != '' else 404,
        })
        await send({
            'type': 'http.response.body',
            'body': body.encode('UTF-8'),
        })

    async def read_body(self, receive):
        """
        Read and return the entire body from an incoming ASGI message.
        """
        body = b''
        more_body = True

        while more_body:
            message = await receive()
            body += message.get('body', b'')
            more_body = message.get('more_body', False)

        if body:
            body = self.parse_body(body)

        return body

    @staticmethod
    def parse_body(body):
        decoded_data = body.decode('UTF-8')
        data_params = decoded_data.split('&')
        body = dict(param.split('=') for param in data_params)
        return body


app = App(api_router=router)
app.api_router.include_routes(auth_router).include_routes(api_router)
