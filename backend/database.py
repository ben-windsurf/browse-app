from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import List, Optional

# User database setup
USER_DATABASE_URL = "sqlite:///./Data/user_data.db"
user_engine = create_engine(USER_DATABASE_URL, connect_args={"check_same_thread": False})
UserSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=user_engine)

# Event database setup
EVENT_DATABASE_URL = "sqlite:///./Data/event_data.db"
event_engine = create_engine(EVENT_DATABASE_URL, connect_args={"check_same_thread": False})
EventSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=event_engine)

# Base classes for each database
UserBase = declarative_base()
EventBase = declarative_base()

# User Database Model
class User(UserBase):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Event Database Model
class Event(EventBase):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    artist = Column(String, index=True)
    date = Column(String)
    venue = Column(String)
    image_url = Column(String, nullable=True)

# Create tables
UserBase.metadata.create_all(bind=user_engine)
EventBase.metadata.create_all(bind=event_engine)

# Database dependencies
def get_user_db():
    db = UserSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_event_db():
    db = EventSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initial event data to populate the database
INITIAL_EVENTS = [
    {
        "id": 1,
        "artist": "Rufus Du Sol",
        "date": "Sat, Jul 26 • 8:00 PM",
        "venue": "Chase Center",
        "image_url": "/assets/artists/rufus.png"
    },
    {
        "id": 2,
        "artist": "Billie Eilish",
        "date": "Sun, Aug 10 • 7:30 PM",
        "venue": "Oracle Park",
        "image_url": "/assets/artists/billie.png"
    },
    {
        "id": 3,
        "artist": "Zach Bryan",
        "date": "Fri, Sep 15 • 8:00 PM",
        "venue": "Shoreline Amphitheatre",
        "image_url": "/assets/artists/zach.png"
    },
    {
        "id": 4,
        "artist": "Lady Gaga",
        "date": "Tue, Jul 22 • 8:00 PM",
        "venue": "SAP Center",
        "image_url": "/assets/artists/gaga.png"
    }
]

# Function to initialize the event database with data
def init_event_db():
    db = EventSessionLocal()
    # Check if events already exist
    existing_events = db.query(Event).first()
    if not existing_events:
        for event_data in INITIAL_EVENTS:
            event = Event(**event_data)
            db.add(event)
        db.commit()
    db.close()
