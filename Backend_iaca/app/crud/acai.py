from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.acai import (
    AcaiLoteCreate, AcaiLoteOut,
    AcaiCarocoCreate, AcaiCarocoOut
)
from app.crud import acai as crud_acai
from app.database import SessionLocal
from app.auth.jwt import get_current_user
from app.models.user import User

router = APIRouter(prefix="/acai", tags=["açai"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/lotes", response_model=AcaiLoteOut)
def registrar_lote(
    lote: AcaiLoteCreate,
    db: Session = Depends(get_db),
    usuario: User = Depends(get_current_user)
):
    return crud_acai.criar_lote(db, lote, usuario.id)

@router.get("/lotes", response_model=list[AcaiLoteOut])
def listar_lotes(db: Session = Depends(get_db)):
    return crud_acai.listar_lotes_disponiveis(db)

@router.post("/comprar/{lote_id}", response_model=AcaiLoteOut)
def comprar_lote(lote_id: int, db: Session = Depends(get_db)):
    lote = crud_acai.comprar_lote(db, lote_id)
    if not lote:
        raise HTTPException(status_code=404, detail="Lote não disponível")
    return lote

@router.post("/carocos", response_model=AcaiCarocoOut)
def criar_caroco(
    caroco_data: AcaiCarocoCreate,
    db: Session = Depends(get_db),
    usuario: User = Depends(get_current_user)
):
    return crud_acai.criar_caroco(db, caroco_data, usuario.id)
