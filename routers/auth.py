from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from schemas.all_schemas import Token, TokenData
from models import all_models
from utils.security import verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Body
from schemas.all_schemas import EmpresaCreate, EmpresaResponse, VendedorCreate, VendedorResponse
from utils.security import hash_password

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(all_models.Empresa).filter(all_models.Empresa.email == form_data.username).first()
    role = "empresa"

    if not user:
        user = db.query(all_models.Vendedor).filter(all_models.Vendedor.email == form_data.username).first()
        role = "vendedor"

    if not user or not verify_password(form_data.password, user.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

    access_token = create_access_token(data={"id": user.id, "role": role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
def registro_usuario(
    tipo: str = Body(...),
    dados: dict = Body(...),
    db: Session = Depends(get_db)
):
    if tipo == "empresa":
        if db.query(all_models.Empresa).filter(all_models.Empresa.email == dados["email"]).first():
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        empresa = all_models.Empresa(
            nome=dados["nome"],
            cnpj=dados["cnpj"],
            email=dados["email"],
            senha_hash=hash_password(dados["senha"]),
            telefone=dados.get("telefone", ""),
            whatsapp=dados.get("whatsapp", False),
            endereco=dados.get("endereco", ""),
            receber_info=dados.get("receber_info", False)
        )
        db.add(empresa)
        db.commit()
        db.refresh(empresa)
        return {"tipo": "empresa", "id": empresa.id}

    elif tipo == "vendedor":
        if db.query(all_models.Vendedor).filter(all_models.Vendedor.email == dados["email"]).first():
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        vendedor = all_models.Vendedor(
            nome=dados["nome"],
            email=dados["email"],
            senha_hash=hash_password(dados["senha"]),
            local_feira=dados.get("local_feira", ""),
            telefone=dados.get("telefone", ""),
            whatsapp=dados.get("whatsapp", False),
            receber_info=dados.get("receber_info", False)
        )
        db.add(vendedor)
        db.commit()
        db.refresh(vendedor)
        return {"tipo": "vendedor", "id": vendedor.id}

    else:
        raise HTTPException(status_code=400, detail="Tipo inválido: use 'empresa' ou 'vendedor'")

