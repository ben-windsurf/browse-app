from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional, List
import os
import secrets

# Import database models and dependencies
from database import User, Event, get_user_db, get_event_db, init_event_db

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Pydantic Models
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class EventResponse(BaseModel):
    id: int
    artist: str
    date: str
    venue: str
    image_url: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class MessageResponse(BaseModel):
    message: str

# Initialize event database if needed
init_event_db()

# FastAPI app
app = FastAPI(title="StubHub Demo API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_reset_token():
    return secrets.token_urlsafe(32)

def send_reset_email(email: str, reset_token: str):
    reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
    print(f"Password reset email for {email}:")
    print(f"Reset link: {reset_link}")
    print("(In production, this would be sent via email service)")
    return True

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db = Depends(get_user_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user



# Routes
@app.get("/")
async def root():
    return {"message": "StubHub Demo API"}

@app.post("/auth/signup", response_model=Token)
async def signup(user: UserCreate, db = Depends(get_user_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin, db = Depends(get_user_db)):
    # Authenticate user
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/forgot-password", response_model=MessageResponse)
async def forgot_password(request: ForgotPasswordRequest, db = Depends(get_user_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        return {"message": "If an account with that email exists, a password reset link has been sent."}
    
    reset_token = generate_reset_token()
    reset_expires = datetime.utcnow() + timedelta(hours=1)
    
    user.reset_token = reset_token
    user.reset_token_expires = reset_expires
    db.commit()
    
    send_reset_email(user.email, reset_token)
    
    return {"message": "If an account with that email exists, a password reset link has been sent."}

@app.post("/auth/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest, db = Depends(get_user_db)):
    user = db.query(User).filter(User.reset_token == request.token).first()
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token"
        )
    
    user.hashed_password = get_password_hash(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return {"message": "Password has been reset successfully."}

@app.get("/events", response_model=List[EventResponse])
async def get_events(db = Depends(get_event_db)):
    """Get all events from the database"""
    events = db.query(Event).all()
    return events

@app.get("/events/protected", response_model=List[EventResponse])
async def get_protected_events(current_user: User = Depends(get_current_user), db = Depends(get_event_db)):
    """Protected endpoint example - requires authentication"""
    events = db.query(Event).all()
    return events

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
