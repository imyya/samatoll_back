import joblib
import pandas as pd
from pathlib import Path

MODEL_DIR = Path(__file__).parent / "models"

model = joblib.load(MODEL_DIR / "best_humidity_model.pkl")
scaler = joblib.load(MODEL_DIR / "scaler.pkl")
encoders = joblib.load(MODEL_DIR / "encoders.pkl")
features = joblib.load(MODEL_DIR / "feature_columns.pkl")
metadata = joblib.load(MODEL_DIR / "model_metadata.pkl")
use_scaler = metadata["use_scaler"]

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