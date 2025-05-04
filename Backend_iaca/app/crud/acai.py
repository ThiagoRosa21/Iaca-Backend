from sqlalchemy.orm import Session
from app.models.acai import AcaiLote
from app.schemas.acai import AcaiLoteCreate

def criar_lote(db: Session, lote: AcaiLoteCreate, vendedor_id: int):
    db_lote = AcaiLote(
        vendedor_id=vendedor_id,
        quantidade_kg=lote.quantidade_kg,
        preco_kg=lote.preco_kg
    )
    db.add(db_lote)
    db.commit()
    db.refresh(db_lote)
    return db_lote

def listar_lotes_disponiveis(db: Session):
    return db.query(AcaiLote).filter(AcaiLote.disponivel == 1).all()

def comprar_lote(db: Session, lote_id: int):
    lote = db.query(AcaiLote).filter(AcaiLote.id == lote_id, AcaiLote.disponivel == 1).first()
    if lote:
        lote.disponivel = 0
        db.commit()
        db.refresh(lote)
    return lote