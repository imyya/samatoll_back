from twilio.rest import Client
from app.ml.predictor import fetch_weather_dakar, predict_humidity
from dotenv import load_dotenv
import os
load_dotenv()

def check_humidity_periodically():
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        alert_phone = os.getenv("ALERT_PHONE")
        
        if not api_key or not alert_phone:
            print("❌ Clés API manquantes – skip")
            return
        
        weather_data = fetch_weather_dakar(api_key)
        print(f"Données OpenWeather: {weather_data}")
        
        humidity = predict_humidity(weather_data)
        print(f"Humidité prédite: {humidity:.1f}%")

        if humidity > 70:
            alert_msg = f"🚨 ALERTE HUMIDITÉ DAKAR: {humidity:.1f}% ! Risque moisissures. Temp: {weather_data['temperature']}°C, Vent: {weather_data['wind_speed']} m/s"
            
            # Envoi SMS
            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            from_number = os.getenv("TWILIO_FROM_NUMBER")
            
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=alert_msg,
                from_=from_number,
                to=alert_phone
            )
            print(f"📱 SMS envoyé ! SID: {message.sid}")
        else:
            print("✅ Pas d'alerte – humidité OK")
    
    except Exception as e:
        print(f"❌ Erreur dans le scheduler: {e}")