# routers/descarte.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.all_models import Descarte, PontoColeta, Vendedor
from schemas.all_schemas import DescarteCreate, DescarteResponse
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=DescarteResponse)
def registrar_descarte(data: DescarteCreate, db: Session = Depends(get_db)):
    vendedor = db.query(Vendedor).filter(Vendedor.id == data.vendedor_id).first()
    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor não encontrado")

    descarte = Descarte(**data.dict())
    vendedor.pontos += 10

    db.add(descarte)
    db.commit()
    db.refresh(descarte)
    return descarte

@router.get("/vendedor/{vendedor_id}", response_model=List[DescarteResponse])
def listar_descartes(vendedor_id: int, db: Session = Depends(get_db)):
    return db.query(Descarte).filter(Descarte.vendedor_id == vendedor_id).all()
