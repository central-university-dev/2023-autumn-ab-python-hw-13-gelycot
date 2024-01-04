from todo_list_app.utils.server import App
from todo_list_app.utils.api_router import router
from todo_list_app.auth import router as auth_router
from todo_list_app.api import router as api_router
from todo_list_app.web import router as web_router

app = App(api_router=router)
app.api_router.include_routes(auth_router).include_routes(
    api_router
).include_routes(web_router)
