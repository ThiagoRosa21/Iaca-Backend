from pydantic import BaseModel
from datetime import datetime

class AcaiLoteCreate(BaseModel):
    quantidade: float
    preco_por_litro: float
    descricao: str | None = None

class AcaiLoteOut(AcaiLoteCreate):
    id: int
    disponivel: bool
    created_at: datetime
    class Config:
        from_attributes = True
