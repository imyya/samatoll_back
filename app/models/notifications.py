from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base


class Notification(Base):
    """Modèle pour stocker les notifications"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    
    message = Column(Text, nullable=True)
    recipient = Column(String(50), nullable=True, index=True)  # Numéro de téléphone ou email
    
    # Type et statut
    # Types possibles: "sms", "email", "push"
    notification_type = Column(String(20), default="sms", nullable=True)
    # Statuts possibles: "pending", "sent", "failed"
    status = Column(String(20), default="pending", nullable=True, index=True)
    
    # Informations Twilio (pour SMS)
    twilio_sid = Column(String(100), nullable=True, index=True)
    
    # Messages d'erreur (en cas d'échec)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.notification_type}, status={self.status}, recipient={self.recipient})>"

