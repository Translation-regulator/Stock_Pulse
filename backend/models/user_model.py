from pydantic import BaseModel

class RegisterForm(BaseModel):
    name: str
    email: str
    password: str

class LoginForm(BaseModel):
    email: str
    password: str
