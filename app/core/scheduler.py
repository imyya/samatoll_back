from twilio.rest import Client
from app.ml.predictor import fetch_weather_dakar, predict_humidity
from app.models.notifications import Notification
from app.db.database import SessionLocal
from dotenv import load_dotenv
from datetime import datetime
import os
load_dotenv()

def check_humidity_periodically():
    db = None
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

        db = SessionLocal()
        
        if humidity > 80:
            alert_msg = f"🚨 ALERTE HUMIDITÉ DAKAR: {humidity:.1f}% ! Risque moisissures. Temp: {weather_data['temperature']}°C, Vent: {weather_data['wind_speed']} m/s"
            
            notification = Notification(
                message=alert_msg,
                recipient=alert_phone,
                notification_type="sms",
                status="pending"
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            print(f"📝 Notification enregistrée dans la DB (ID: {notification.id})")
            
            try:
                # Envoi SMS
                account_sid = os.getenv("TWILIO_ACCOUNT_SID")
                auth_token = os.getenv("TWILIO_AUTH_TOKEN")
                from_number = os.getenv("TWILIO_FROM_NUMBER")
                
                if not account_sid or not auth_token or not from_number:
                    raise Exception("Twilio credentials manquantes")
                
                client = Client(account_sid, auth_token)
                twilio_message = client.messages.create(
                    body=alert_msg,
                    from_=from_number,
                    to=alert_phone
                )
                
                # Mettre à jour la notification : statut = sent, twilio_sid, sent_at
                notification.status = "sent"
                notification.twilio_sid = twilio_message.sid
                notification.sent_at = datetime.now()
                db.commit()
                
                print(f"📱 SMS envoyé ! SID: {twilio_message.sid}")
            except Exception as sms_error:
                # En cas d'erreur lors de l'envoi, mettre à jour le statut à "failed"
                notification.status = "failed"
                notification.error_message = str(sms_error)
                db.commit()
                print(f"❌ Erreur lors de l'envoi SMS: {sms_error}")
        else:
            print("✅ Pas d'alerte – humidité OK")
    
    except Exception as e:
        print(f"❌ Erreur dans le scheduler: {e}")
        # Si une notification était créée mais qu'une erreur survient, la marquer comme failed
        if db:
            try:
                db.rollback()
            except:
                pass
    finally:
        # Fermer la session de base de données
        if db:
            db.close()