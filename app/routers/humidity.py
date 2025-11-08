from fastapi import APIRouter, HTTPException
from app.ml.predictor import predict_humidity
from pydantic import BaseModel
router = APIRouter(prefix="/humidity", tags=["humidity"])
from app.ml.predictor import fetch_weather_dakar, predict_humidity
import os
from twilio.rest import Client
from app.core.scheduler import check_humidity_periodically
# from main import check_humidity_periodically
class HumidityInput(BaseModel):
    region: str
    departement: str
    weather: str
    temperature: float
    wind_speed: float
    date: str  # "2025-06-15 14:00:00"

@router.post("/predict")
def predict(input: HumidityInput):
    try:
        humidity = predict_humidity(input.dict())
        humidity_rounded = round(humidity,1)
        if humidity_rounded > 80:
            alert = "ALERTE : Humidité très élevée – risque de moisissures"
            level = "danger"
        elif humidity_rounded > 70:
            alert = "Attention : Humidité élevée"
            level = "warning"
        elif humidity_rounded > 50:
            alert = "Niveau normal"
            level = "success"
        else:
            alert = "Humidité basse – risque de sécheresse"
            level = "info"

        return {
            "humidity": humidity_rounded,
            "alert": alert,
            "level": level
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/check-dakar-now")
def check_dakar_now():
    """Test manuel: fetch + predict + alert pour Dakar"""
    check_humidity_periodically()  # Utilise la même fonction
    return {"status": "Check lancé – vérifie les logs"}