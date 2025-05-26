# schemas/all_schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None
    role: Optional[str] = None


class EmpresaBase(BaseModel):
    nome: str
    cnpj: str
    email: EmailStr
    telefone: str
    whatsapp: Optional[bool] = False
    endereco: str
    receber_info: Optional[bool] = False

class EmpresaCreate(EmpresaBase):
    senha: str

class EmpresaResponse(EmpresaBase):
    id: int

    class Config:
        orm_mode = True

class VendedorBase(BaseModel):
    nome: str
    email: EmailStr
    local_feira: str
    telefone: str
    whatsapp: Optional[bool] = False
    receber_info: Optional[bool] = False

class VendedorCreate(VendedorBase):
    senha: str

class VendedorResponse(VendedorBase):
    id: int
    pontos: int

    class Config:
        orm_mode = True


class PontoBase(BaseModel):
    nome: str
    endereco: str
    lat: float
    lng: float
    status: Optional[str] = "ativo"

class PontoCreate(PontoBase):
    empresa_id: int

class PontoResponse(PontoBase):
    id: int

    class Config:
        orm_mode = True


class DescarteCreate(BaseModel):
    vendedor_id: int
    ponto_id: int
    quantidade_kg: float
    foto_url: Optional[str] = None

class DescarteResponse(BaseModel):
    id: int
    data_hora: datetime
    quantidade_kg: float
    foto_url: Optional[str]
    ponto: PontoResponse

    class Config:
        orm_mode = True
        
class PagamentoCreate(BaseModel):
    empresa_id: int
    valor_centavos: int

class PagamentoResponse(BaseModel):
    id: int
    stripe_session_id: str
    status: str
    valor_centavos: int
    data_pagamento: datetime
    metodo_pagamento: Optional[str] = "card"
    nota_fiscal_hash: Optional[str] = None
    class Config:
        from_attributes = True 