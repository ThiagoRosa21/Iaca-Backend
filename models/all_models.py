
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
    rotas = relationship("Rota", back_populates="empresa")
    pagamentos = relationship("Pagamento", back_populates="empresa")
    email_verificado = Column(Boolean, default=False)
    codigo_verificacao = Column(String, nullable=True)
    codigo_verificacao_expira_em = Column(DateTime, nullable=True)
    
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
    email_verificado = Column(Boolean, default=False)
    codigo_verificacao = Column(String, nullable=True)
    descartes = relationship("Descarte", back_populates="vendedor")
    codigo_verificacao_expira_em = Column(DateTime, nullable=True)

class PontoColeta(Base):
    __tablename__ = "pontos_coleta"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    endereco = Column(String, nullable=False)
    lat = Column(Float)
    lng = Column(Float)
    status = Column(String, default="ativo")
    descartes = relationship("Descarte", back_populates="ponto")
    historico_valores = relationship("HistoricoValorKG", back_populates="ponto")
    


class Descarte(Base):
    __tablename__ = "descartes"
    id = Column(Integer, primary_key=True, index=True)
    vendedor_id = Column(Integer, ForeignKey("vendedores.id"))
    ponto_id = Column(Integer, ForeignKey("pontos_coleta.id"))
    quantidade_kg = Column(Float)
    data_hora = Column(DateTime, default=datetime.utcnow)
    foto_url = Column(String, nullable=True)
    comprado = Column(Boolean, default=False) 
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
    ponto_id = Column(Integer, ForeignKey("pontos_coleta.id"), nullable=True)
    
class Rota(Base):
    __tablename__ = "rotas"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    origem_lat = Column(Float, nullable=False)
    origem_lng = Column(Float, nullable=False)
    destino_lat = Column(Float, nullable=False)
    destino_lng = Column(Float, nullable=False)
    distancia_km = Column(Float, nullable=False)
    duracao_min = Column(Float, nullable=False)
    data_registro = Column(DateTime, default=datetime.utcnow)

    empresa = relationship("Empresa", back_populates="rotas")
    
    
class HistoricoValorKG(Base):
    __tablename__ = "historico_valor_kg"
    id = Column(Integer, primary_key=True, index=True)
    ponto_id = Column(Integer, ForeignKey("pontos_coleta.id"), nullable=False)
    valor_por_kg = Column(Float, nullable=False)
    data_inicio = Column(DateTime, default=datetime.utcnow)
    data_fim = Column(DateTime, nullable=True)

    ponto = relationship("PontoColeta", back_populates="historico_valores")



