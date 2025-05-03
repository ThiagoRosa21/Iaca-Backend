from sqlalchemy.orm import Session
from app.models.acai import AcaiLote
from app.schemas.acai import AcaiLoteCreate

def criar_lote(db: Session, lote: AcaiLoteCreate, user_id: int):
    novo_lote = AcaiLote(**lote.model_dump(), vendedor_id=user_id)
    db.add(novo_lote)
    db.commit()
    db.refresh(novo_lote)
    return novo_lote

def listar_lotes_disponiveis(db: Session):
    return db.query(AcaiLote).filter(AcaiLote.disponivel == True).all()
