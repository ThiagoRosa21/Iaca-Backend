from pydantic import BaseModel
from typing import Optional

class AcaiLoteCreate(BaseModel):
    quantidade_kg: float
    preco_kg: float

class AcaiLoteOut(BaseModel):
    id: int
    vendedor_id: int
    quantidade_kg: float
    preco_kg: float
    disponivel: int

    class Config:
        from_attributes = True