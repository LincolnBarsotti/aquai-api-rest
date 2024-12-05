import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from pathlib import Path
import numpy as np
from passlib.context import CryptContext
import models
from database import SessionLocal, engine
from dto import CadastroRequest, LoginRequest
from PIL import Image
from fastapi.middleware.cors import CORSMiddleware

# Configuração do FastAPI
app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite requisições de todas as origens (modifique conforme necessário)
    allow_credentials=True,  # Permite envio de cookies e headers de autenticação
    allow_methods=["*"],  # Permite todos os métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os headers
)

# Configuração do Hashing de Senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Inicializa o banco de dados
models.Base.metadata.create_all(bind=engine)

# Configuração de uploads
UPLOAD_FOLDER = Path("uploads")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Carregando o modelo de classificação
model = None
class_labels = ['mamiferos', 'peixes', 'plantas']  # Atualize com suas classes


# Função para carregar o modelo uma vez na inicialização
@app.on_event("startup")
def load_classification_model():
    global model
    model = load_model('modelo_classificacao_animais.h5')


# Dependência para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Função auxiliar para hash de senha
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Função auxiliar para verificar senha
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Função para verificar o tipo de arquivo
def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Rota inicial
@app.get("/")
async def root():
    return {"message": "API está funcionando!"}


# Endpoint para cadastro de usuário
@app.post("/cadastro", status_code=status.HTTP_201_CREATED)
def cadastro(request: CadastroRequest, db: Session = Depends(get_db)):
    # Verifica se o email já está registrado
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # Cria um novo usuário com senha hasheada
    new_user = models.User(
        nome=request.nome,
        email=request.email,
        password=hash_password(request.password),  # Hashing da senha
        data_nascimento=request.data_nascimento
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Usuário registrado com sucesso", "user_id": new_user.id}


# Endpoint para login
@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Busca o usuário pelo email
    user = db.query(models.User).filter(models.User.email == request.email).first()

    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=400, detail="Email ou senha inválidos")

    return {"message": "Login bem-sucedido", "user_id": user.id}


# Endpoint para upload e predição
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Verifica se o arquivo é permitido
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Arquivo inválido. Permitidos: png, jpg, jpeg.")

    # Salva o arquivo na pasta de uploads
    filepath = UPLOAD_FOLDER / file.filename
    try:
        with open(filepath, "wb") as buffer:
            buffer.write(await file.read())

        # Pré-processa a imagem
        img = load_img(filepath, target_size=(32, 32))  # Atualize para o tamanho do seu modelo
        img_array = img_to_array(img) / 255.0  # Normaliza a imagem
        img_array = np.expand_dims(img_array, axis=0)  # Adiciona uma dimensão extra para o batch

        # Faz a predição
        predictions = model.predict(img_array)
        predicted_class = class_labels[np.argmax(predictions)]
        confidence = float(np.max(predictions))

        # Retorna a resposta
        return JSONResponse(content={"class": predicted_class, "confidence": confidence})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro durante a predição: {str(e)}")

    finally:
        # Remove o arquivo após a predição
        filepath.unlink(missing_ok=True)
