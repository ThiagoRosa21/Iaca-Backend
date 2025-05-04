from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class AcaiLote(Base):
    __tablename__ = "acai_lotes"

    id = Column(Integer, primary_key=True, index=True)
    vendedor_id = Column(Integer, ForeignKey("users.id"))
    quantidade_kg = Column(Float, nullable=False)
    preco_kg = Column(Float, nullable=False)
    disponivel = Column(Integer, default=1)  # 1: disponível, 0: vendido
    criado_em = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="lotes")

    vendedor = relationship("User", back_populates="lotes")