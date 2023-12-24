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
