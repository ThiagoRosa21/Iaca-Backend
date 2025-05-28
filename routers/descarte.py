# routers/descarte.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.all_models import Descarte, PontoColeta, Vendedor
from schemas.all_schemas import DescarteCreate, DescarteResponse
from typing import List

VALOR_KG_PADRAO = 50 / 1000  

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=DescarteResponse)
def registrar_descarte(data: DescarteCreate, db: Session = Depends(get_db)):
    vendedor = db.query(Vendedor).filter(Vendedor.id == data.vendedor_id).first()
    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor não encontrado")

    descarte = Descarte(**data.dict())
    vendedor.pontos += 10

    db.add(descarte)
    db.commit()
    db.refresh(descarte)
    return descarte

@router.get("/vendedor/{vendedor_id}", response_model=List[DescarteResponse])
def listar_descartes(vendedor_id: int, db: Session = Depends(get_db)):
    descartes = db.query(Descarte).filter(Descarte.vendedor_id == vendedor_id).all()

    resultados = []
    for d in descartes:
        ponto = db.query(PontoColeta).filter(PontoColeta.id == d.ponto_id).first()
        valor_kg = 0
        if ponto and ponto.historico_valores:
            historico = sorted(ponto.historico_valores, key=lambda h: h.data_inicio, reverse=True)
            valor_kg = historico[0].valor_por_kg
        valor_estimado = d.quantidade_kg * valor_kg

        resultados.append({
            "id": d.id,
            "data_hora": d.data_hora,
            "quantidade_kg": d.quantidade_kg,
            "foto_url": d.foto_url,
            "ponto": d.ponto,
            "valor_estimado": valor_estimado
        })

    return resultados

@router.get("/ponto/{ponto_id}/resumo")
def resumo_ponto(ponto_id: int, db: Session = Depends(get_db)):
    ponto = db.query(PontoColeta).filter(PontoColeta.id == ponto_id).first()
    if not ponto:
        raise HTTPException(status_code=404, detail="Ponto não encontrado")

    # ✅ Filtra apenas descartes ainda não comprados
    descartes = db.query(Descarte).filter(
        Descarte.ponto_id == ponto_id,
        Descarte.comprado == False
    ).all()

    total_kg = sum(d.quantidade_kg or 0 for d in descartes)

    historico = sorted(ponto.historico_valores, key=lambda h: h.data_inicio, reverse=True)
    valor_kg = historico[0].valor_por_kg if historico else VALOR_KG_PADRAO
    valor_total = total_kg * valor_kg

    return {
        "ponto_id": ponto.id,
        "nome": ponto.nome,
        "total_kg": total_kg,
        "valor_kg_atual": valor_kg,
        "valor_estimado_total": round(valor_total, 2)
    }
    
@router.post("/compra/{ponto_id}", summary="Comprar caroço de açaí de um ponto de descarte")
def comprar_caroco(ponto_id: int, db: Session = Depends(get_db)):
    ponto = db.query(PontoColeta).filter(PontoColeta.id == ponto_id).first()
    if not ponto:
        raise HTTPException(status_code=404, detail="Ponto não encontrado")

    descartes = db.query(Descarte).filter(Descarte.ponto_id == ponto_id).all()
    total_kg = sum(d.quantidade_kg or 0 for d in descartes)

    if total_kg <= 0:
        raise HTTPException(status_code=400, detail="Este ponto de descarte não possui caroço de açaí disponível para compra.")

    # Se houver disponibilidade, prossiga com a lógica de criação do pagamento
    return {"mensagem": f"Compra iniciada com {total_kg:.2f} kg disponíveis."}