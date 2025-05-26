# routers/rota.py
from fastapi import APIRouter, HTTPException
from schemas.all_schemas import RotaRequest, RotaResponse
from services.mapbox_service import calcular_rota_mapbox as calcular_rota_mapbox_service

router = APIRouter()

@router.post("/rota", response_model=RotaResponse, summary="Calcula a rota entre dois pontos usando Mapbox")
def calcular_rota_mapbox(payload: RotaRequest):
    try:
        return calcular_rota_mapbox_service(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
