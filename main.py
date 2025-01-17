import os
import base64
import logging
import sys
from datetime import datetime
from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: `DATABASE_URL` is not set. Please check Render's environment variables.")
    sys.exit(1)

# Convert old `postgres://` to `postgresql://`
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

# Debugging: Print DATABASE_URL
print("✅ DATABASE_URL Loaded:", DATABASE_URL)

engine = create_engine(DATABASE_URL)

# Session handling
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Ensure tables are created when the app starts
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- FastAPI App ---
app = FastAPI()

# --- Database Model ---
class Event(Base):
    __tablename__ = "clicks"  # Keep your existing table name

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    ip = Column(String, nullable=False)
    event_type = Column(String, nullable=False)  # 'open' or 'click'
    timestamp = Column(DateTime, default=datetime.utcnow)

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1x1 Transparent GIF (Base64 Encoded) ---
ONE_PIXEL_GIF_BASE64 = "R0lGODlhAQABAPAAAAAAAAAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=="
ONE_PIXEL_GIF = base64.b64decode(ONE_PIXEL_GIF_BASE64)

# --- Root Endpoint ---
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Email Tracker API. Use /track_email?email=youremail@example.com to track email clicks."
    }

# --- Track Email Open ---
@app.get("/track_open")
def track_open(request: Request, email: str = "", db: Session = Depends(get_db)):
    client_ip = request.client.host
    logger.info(f"Email opened by: {email} from IP: {client_ip}")

    # Log event to database
    event = Event(email=email, ip=client_ip, event_type="open")
    db.add(event)
    db.commit()
    db.refresh(event)

    # Return 1x1 Transparent GIF
    return Response(content=ONE_PIXEL_GIF, media_type="image/gif")

# --- Track Link Click ---
@app.get("/track_click")
def track_click(request: Request, email: str = "", db: Session = Depends(get_db)):
    client_ip = request.client.host
    logger.info(f"Link clicked by: {email} from IP: {client_ip}")

    # Log event to database
    event = Event(email=email, ip=client_ip, event_type="click")
    db.add(event)
    db.commit()
    db.refresh(event)

    # Redirect to the actual signup page
    return RedirectResponse(url=f"https://yourcourse.com/signup?email={email}")

# --- Retrieve Click Data ---
@app.get("/clicks")
def get_clicks(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    return [
        {
            "id": event.id,
            "email": event.email,
            "ip": event.ip,
            "event_type": event.event_type,
            "timestamp": event.timestamp,
        }
        for event in events
    ]
