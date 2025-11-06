from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI
from app.db.database import Base, engine
from app.models import user
from app.routers import users, notifications

app = FastAPI()
Base.metadata.create_all(bind=engine)

#   app.include_router(users.router)
app.include_router(notifications.router)    

@app.get("/health")
def health():
    return {"status": "ok working girl"}