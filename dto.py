from pydantic import BaseModel

# DTO para a requisição de login
class LoginRequest(BaseModel):
    email: str
    password: str
