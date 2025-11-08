import joblib
import pandas as pd
from pathlib import Path
from datetime import datetime
import requests
MODEL_DIR = Path(__file__).parent / "models"

model = joblib.load(MODEL_DIR / "best_humidity_model.pkl")
scaler = joblib.load(MODEL_DIR / "scaler.pkl")
encoders = joblib.load(MODEL_DIR / "encoders.pkl")
features = joblib.load(MODEL_DIR / "feature_columns.pkl")
metadata = joblib.load(MODEL_DIR / "model_metadata.pkl")
use_scaler = metadata["use_scaler"]

def fetch_weather_dakar(api_key: str):
    """Récupère les données météo actuelles pour Dakar depuis OpenWeatherMap"""
    print("la api key openweather",api_key)
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Dakar,SN&appid={api_key}&units=metric"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Erreur API OpenWeather: {response.status_code}")
    
    data = response.json()
    
    # Mapper la météo à notre format (simplifié)
    weather_main = data['weather'][0]['main'].lower()
    weather_desc = data['weather'][0]['description'].lower()
    
    # Mapping vers nos catégories (ajuste selon tes besoins)
    if 'rain' in weather_desc or 'rain' in weather_main:
        weather = 'light rain' if data.get('rain', {}).get('1h', 0) < 2.5 else 'heavy rain'
    elif 'thunderstorm' in weather_desc:
        weather = 'thunderstorm with rain'
    elif 'clouds' in weather_main:
        if 'clear' in weather_desc:
            weather = 'clear sky'
        else:
            weather = 'scattered clouds'  # Simplifié
    else:
        weather = 'clear sky'  # Défaut
    
    return {
        'region': 'Dakar',
        'departement': 'Dakar',
        'weather': weather,
        'temperature': data['main']['temp'],
        'wind_speed': data['wind']['speed'],
        'date': datetime.now().isoformat()  # Date actuelle UTC
    }

def predict_humidity(data: dict)->float:
    ""'gets a dict and returns the predcited humidity'""
    df = pd.DataFrame([data])
    df['date'] = pd.to_datetime(df['date'])
    df['mois'] = df['date'].dt.month
    df['jour'] = df['date'].dt.day
    df['heure'] = df['date'].dt.hour

    df['region_code'] = df['region'].map(encoders['region_dict'])
    df['departement_code'] = df['departement'].map(encoders['departement_dict'])
    df['weather_code'] = df['weather'].apply(lambda x: encoders['weather_order'].get(x, 4))
    X = df[features]
    if use_scaler:
        X = scaler.transform(X)

    return float(model.predict(X)[0])