# routers/empresa.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.all_models import Empresa, PontoColeta
from schemas.all_schemas import EmpresaCreate, EmpresaResponse, PontoCreate, PontoResponse
from utils.security import hash_password
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=EmpresaResponse)
def criar_empresa(dados: EmpresaCreate, db: Session = Depends(get_db)):
    if db.query(Empresa).filter(Empresa.email == dados.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    empresa = Empresa(
        nome=dados.nome,
        cnpj=dados.cnpj,
        email=dados.email,
        senha_hash=hash_password(dados.senha),
        telefone=dados.telefone,
        whatsapp=dados.whatsapp,
        endereco=dados.endereco,
        receber_info=dados.receber_info
    )
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return empresa

@router.post("/ponto", response_model=PontoResponse)
def criar_ponto(ponto: PontoCreate, db: Session = Depends(get_db)):
    novo_ponto = PontoColeta(**ponto.dict())
    db.add(novo_ponto)
    db.commit()
    db.refresh(novo_ponto)
    return novo_ponto

@router.get("/pontos", response_model=List[PontoResponse])
def listar_pontos(db: Session = Depends(get_db)):
    return db.query(PontoColeta).all()
