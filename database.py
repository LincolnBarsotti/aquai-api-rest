from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import urllib.parse

# Configurações individuais da conexão
DB_USER = "root"
DB_PASSWORD = "Test@123"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "deepblue"

# Codifica a senha para evitar problemas com caracteres especiais
encoded_password = urllib.parse.quote_plus(DB_PASSWORD)

# Monta a URL de conexão
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configuração do SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
