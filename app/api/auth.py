from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from passlib.context import CryptContext
from app.core.security import create_access_token
from app.core.security import create_access_token, get_current_user
from fastapi import APIRouter, Depends, HTTPException
from app.core.email import generate_verification_token, send_verification_email

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    verification_token = generate_verification_token()
    
    new_user = User(
        email=user.email,
        password=hashed_password,
        verification_token=verification_token
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    await send_verification_email(new_user.email, verification_token)
    
    return new_user

@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    
    existing_user = db.query(User).filter(User.email == user.email).first()
    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not pwd_context.verify(user.password, existing_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token(data={"sub": existing_user.email})
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me")
def get_me(current_user: str = Depends(get_current_user)):
    return {"email": current_user, "message": "You are logged in"}

@router.get("/verify/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.verification_token == token).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    
    user.is_verified = True
    user.verification_token = None
    db.commit()
    
    return {"message": "Email verified successfully. You can now login."}