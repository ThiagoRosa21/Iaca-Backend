# routers/vendedor.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.all_models import Vendedor
from schemas.all_schemas import VendedorCreate, VendedorResponse
from utils.security import hash_password

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=VendedorResponse)
def criar_vendedor(dados: VendedorCreate, db: Session = Depends(get_db)):
    if db.query(Vendedor).filter(Vendedor.email == dados.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    vendedor = Vendedor(
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_password(dados.senha),
        local_feira=dados.local_feira,
        telefone=dados.telefone,
        whatsapp=dados.whatsapp,
        receber_info=dados.receber_info,
    )
    db.add(vendedor)
    db.commit()
    db.refresh(vendedor)
    return vendedor
