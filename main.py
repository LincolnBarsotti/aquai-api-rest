from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine
from dto import CadastroRequest, LoginRequest # Importando o novo DTO

app = FastAPI()

# Criar todas as tabelas do banco de dados
models.Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Dependência para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint para cadastro de usuário
@app.post("/cadastro", status_code=status.HTTP_201_CREATED)  # Usando status importado
def cadastro(request: CadastroRequest, db: Session = Depends(get_db)):
    # Verifica se o email já existe no banco
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # Cria um novo usuário no banco
    new_user = models.User(
        nome=request.nome,
        email=request.email,
        password=request.password,
        data_nascimento=request.data_nascimento
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Usuário registrado com sucesso", "user_id": new_user.id}


@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Verifica se o usuário existe no banco de dados com o email informado
    user = db.query(models.User).filter(models.User.email == request.email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Email ou senha inválidos")

    # Verifica se a senha fornecida corresponde à senha do banco de dados
    if user.password != request.password:
        raise HTTPException(status_code=400, detail="Email ou senha inválidos")

    return {"message": "Login bem-sucedido", "user_id": user.id}