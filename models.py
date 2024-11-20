from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Modelo para a tabela de usuários
class User(Base):
    __tablename__ = "users"  # Nome da tabela no banco de dados

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)  # Novo campo para o nome
    email = Column(String(255), unique=True, index=True, nullable=False)  # Definir comprimento
    password = Column(String(255), nullable=False)  # Definir comprimento
    data_nascimento = Column(Date, nullable=False)  # Novo campo para a data de nascimento
