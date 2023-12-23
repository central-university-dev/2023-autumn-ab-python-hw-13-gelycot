class App:
    async def __call__(self, scope, receive, send):
        """
        Echo the method and path back in an HTTP response.
        """
        assert scope['type'] == 'http'
        if scope['path'] == '/':
            body = 'Simple path'
        else:
            body = 'Difficult path'
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                [b'content-type', b'text/plain'],
            ]
        })
        await send({
            'type': 'http.response.body',
            'body': body.encode('utf-8'),
        })


app = App()