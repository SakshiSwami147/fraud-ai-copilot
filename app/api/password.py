from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.core.email import generate_verification_token, send_verification_email
from app.api.auth import pwd_context
from pydantic import BaseModel

router = APIRouter()

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        return {"message": "If this email exists, a reset link has been sent"}
    
    reset_token = generate_verification_token()
    user.verification_token = reset_token
    db.commit()
    
    reset_link = f"http://127.0.0.1:8000/auth/reset-password?token={reset_token}"
    await send_verification_email(user.email, reset_token)
    
    return {"message": "If this email exists, a reset link has been sent"}

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == request.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    user.password = pwd_context.hash(request.new_password)
    user.verification_token = None
    db.commit()
    
    return {"message": "Password reset successfully. You can now login."}