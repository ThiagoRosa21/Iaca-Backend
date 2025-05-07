from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.acai import AcaiLoteCreate, AcaiLoteOut
from app.crud import acai
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
    return acai.criar_lote(db, lote, usuario.id)

@router.get("/lotes", response_model=list[AcaiLoteOut])
def listar_lotes(db: Session = Depends(get_db)):
    return acai.listar_lotes_disponiveis(db)

@router.post("/comprar/{lote_id}", response_model=AcaiLoteOut)
def comprar_lote(lote_id: int, db: Session = Depends(get_db)):
    lote = acai.comprar_lote(db, lote_id)
    if not lote:
        raise HTTPException(status_code=404, detail="Lote não disponível")
    return lote