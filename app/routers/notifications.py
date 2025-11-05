from fastapi import APIRouter, HTTPException
import os
try:
    from twilio.rest import Client
except Exception:
    Client = None

router = APIRouter(prefix="/notifications")

@router.post("/send_sms/")
async def send_sms(message: str, to: str):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
    from_number = os.getenv("TWILIO_FROM_NUMBER", "")

    if not account_sid or not auth_token or not from_number:
        raise HTTPException(status_code=500, detail="Twilio credentials or from number not configured")

    if Client is None:
        raise HTTPException(status_code=500, detail="twilio package is not installed; please pip install twilio")

    client = Client(account_sid, auth_token)
    sms = client.messages.create(body=message, from_=from_number, to=to)
    return {"sid": sms.sid}