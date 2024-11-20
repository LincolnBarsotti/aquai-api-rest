from fastapi import FastAPI, HTTPException, Depends, status  # Importando status
from sqlalchemy.orm import Session
import models
from database import SessionLocal, Base, engine
from dto import LoginRequest  # Importando o DTO

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

# Endpoint para login
@app.post("/login", status_code=status.HTTP_201_CREATED)  # Usando status importado
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Verifica se o email já existe no banco
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # Cria um novo usuário no banco
    new_user = models.User(email=request.email, password=request.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Usuário registrado com sucesso", "user_id": new_user.id}
