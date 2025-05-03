from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class AcaiLote(Base):
    __tablename__ = "acai_lotes"

    id = Column(Integer, primary_key=True, index=True)
    vendedor_id = Column(Integer, ForeignKey("users.id"))
    quantidade = Column(Float)
    preco_por_litro = Column(Float)
    descricao = Column(String, nullable=True)
    disponivel = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    vendedor = relationship("User", back_populates="acai_lotes")
