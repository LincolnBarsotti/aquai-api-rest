from pydantic import BaseModel
from datetime import date  # Importando o tipo 'date' de 'datetime'

# DTO para a requisição de cadastro de usuário
class CadastroRequest(BaseModel):
    nome: str
    email: str
    password: str
    data_nascimento: date  # Agora o 'date' está definido corretamente

class LoginRequest(BaseModel):
    email: str
    password: str