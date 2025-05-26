# services/mapbox_service.py
import os
import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from schemas.all_schemas import RotaRequest

load_dotenv()

MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")

router = APIRouter()

@router.post("/api/rota", summary="Calcula a rota entre dois pontos usando Mapbox")
def calcular_rota_mapbox(payload: RotaRequest):
    origem = payload.origem
    destino = payload.destino

    url = (
        f"https://api.mapbox.com/directions/v5/mapbox/driving/"
        f"{origem.lng},{origem.lat};{destino.lng},{destino.lat}"
        f"?geometries=geojson&access_token={MAPBOX_API_KEY}"
    )

    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao buscar rota no Mapbox")

    data = response.json()
    rota = data["routes"][0]

    return {
        "distancia_km": rota["distance"] / 1000,
        "duracao_min": rota["duration"] / 60,
        "caminho_geojson": rota["geometry"]
    }
