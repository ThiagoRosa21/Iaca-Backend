
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Empresa(Base):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cnpj = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    telefone = Column(String)
    whatsapp = Column(Boolean, default=False)
    endereco = Column(String)
    receber_info = Column(Boolean, default=False)

    pontos_coleta = relationship("PontoColeta", back_populates="empresa")
    pagamentos = relationship("Pagamento", back_populates="empresa")


class Vendedor(Base):
    __tablename__ = "vendedores"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    local_feira = Column(String)
    telefone = Column(String)
    whatsapp = Column(Boolean, default=False)
    receber_info = Column(Boolean, default=False)
    pontos = Column(Integer, default=0)

    descartes = relationship("Descarte", back_populates="vendedor")


class PontoColeta(Base):
    __tablename__ = "pontos_coleta"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    endereco = Column(String, nullable=False)
    lat = Column(Float)
    lng = Column(Float)
    status = Column(String, default="ativo")
    empresa_id = Column(Integer, ForeignKey("empresas.id"))

    empresa = relationship("Empresa", back_populates="pontos_coleta")
    descartes = relationship("Descarte", back_populates="ponto")


class Descarte(Base):
    __tablename__ = "descartes"
    id = Column(Integer, primary_key=True, index=True)
    vendedor_id = Column(Integer, ForeignKey("vendedores.id"))
    ponto_id = Column(Integer, ForeignKey("pontos_coleta.id"))
    quantidade_kg = Column(Float)
    data_hora = Column(DateTime, default=datetime.utcnow)
    foto_url = Column(String, nullable=True)

    vendedor = relationship("Vendedor", back_populates="descartes")
    ponto = relationship("PontoColeta", back_populates="descartes")


class Pagamento(Base):
    __tablename__ = "pagamentos"
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    valor_centavos = Column(Integer, nullable=False)
    status = Column(String, default="pendente")
    stripe_session_id = Column(String, unique=True, nullable=False)
    data_pagamento = Column(DateTime, default=datetime.utcnow)
    metodo_pagamento = Column(String, default="card")
    empresa = relationship("Empresa", back_populates="pagamentos")
    nota_fiscal_hash = Column(String, nullable=True)

