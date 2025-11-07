from fastapi import APIRouter, HTTPException
from app.ml.predictor import predict_humidity
from pydantic import BaseModel
router = APIRouter(prefix="/humidity", tags=["humidity"])

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
        return {"humidity": round(humidity, 1)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))