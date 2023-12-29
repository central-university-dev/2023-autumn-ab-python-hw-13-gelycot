from pydantic import BaseModel


class RegisterUser(BaseModel):
    username: str
    password: str


class LoginUser(BaseModel):
    username: str
    password: str


class RegisterUserResponse(BaseModel):
    id: int
    username: str


class CreateTaskList(BaseModel):
    name: str


class CreateTask(BaseModel):
    list_id: int
    name: str


class UpdateTaskList(BaseModel):
    name: str
    list_id: int


class UpdateTask(BaseModel):
    name: str
    task_id: int
