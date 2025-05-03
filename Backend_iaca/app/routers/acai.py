from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.acai import AcaiLoteCreate, AcaiLoteOut
from app.crud.acai import criar_lote
from app.database import SessionLocal
from app.models.user import User
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/acai", tags=["acai"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/lotes", response_model=AcaiLoteOut)
def criar_lote(
    lote: AcaiLoteCreate,
    db: Session = Depends(get_db),
    usuario: User = Depends(get_current_user)
):
    return criar_lote(db, lote, usuario.id)
