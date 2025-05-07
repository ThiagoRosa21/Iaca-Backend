from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AcaiLoteCreate(BaseModel):
    quantidade_kg: float
    preco_kg: float


class AcaiLoteOut(BaseModel):
    id: int
    quantidade_kg: float
    preco_kg: float
    disponivel: int
    criado_em: datetime
    vendedor_id: int

    class Config:
        from_attributes = True


class AcaiCarocoCreate(BaseModel):
    quantidade_kg: float
    
class AcaiCarocoOut(BaseModel):
    id: int
    quantidade_kg: float
    vendedor_id: int

    class Config:
        from_attributes = True

