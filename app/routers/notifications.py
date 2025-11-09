from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.notifications import Notification
from datetime import datetime
import os
try:
    from twilio.rest import Client
except Exception:
    Client = None

router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_db():
    """Dependency pour obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/send_sms/")
async def send_sms(message: str, to: str, db: Session = Depends(get_db)):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
    from_number = os.getenv("TWILIO_FROM_NUMBER", "")

    if not account_sid or not auth_token or not from_number:
        raise HTTPException(status_code=500, detail="Twilio credentials or from number not configured")

    if Client is None:
        raise HTTPException(status_code=500, detail="twilio package is not installed; please pip install twilio")

    # Créer l'enregistrement de notification dans la base de données (statut: pending)
    notification = Notification(
        message=message,
        recipient=to,
        notification_type="sms",
        status="pending"
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    try:
        # Envoi SMS
        client = Client(account_sid, auth_token)
        sms = client.messages.create(body=message, from_=from_number, to=to)
        
        # Mettre à jour la notification : statut = sent, twilio_sid, sent_at
        notification.status = "sent"
        notification.twilio_sid = sms.sid
        notification.sent_at = datetime.now()
        db.commit()
        
        return {
            "sid": sms.sid,
            "notification_id": notification.id,
            "status": "sent"
        }
    except Exception as e:
        # En cas d'erreur lors de l'envoi, mettre à jour le statut à "failed"
        notification.status = "failed"
        notification.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi SMS: {str(e)}")


@router.get("/")
async def get_notifications(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    Récupère la liste des notifications avec possibilité de filtrer par statut
    """
    query = db.query(Notification)
    
    if status:
        query = query.filter(Notification.status == status)
    
    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": len(notifications),
        "notifications": [
            {
                "id": notif.id,
                "message": notif.message,
                "recipient": notif.recipient,
                "notification_type": notif.notification_type,
                "status": notif.status,
                "twilio_sid": notif.twilio_sid,
                "error_message": notif.error_message,
                "created_at": notif.created_at.isoformat() if notif.created_at else None,
                "sent_at": notif.sent_at.isoformat() if notif.sent_at else None
            }
            for notif in notifications
        ]
    }

@router.get("/{notification_id}")
async def get_notification(notification_id: int, db: Session = Depends(get_db)):
    """
    Récupère une notification spécifique par son ID
    """
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {
        "id": notification.id,
        "message": notification.message,
        "recipient": notification.recipient,
        "notification_type": notification.notification_type,
        "status": notification.status,
        "twilio_sid": notification.twilio_sid,
        "error_message": notification.error_message,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
        "sent_at": notification.sent_at.isoformat() if notification.sent_at else None
    }