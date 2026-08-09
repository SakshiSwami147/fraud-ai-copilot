import secrets
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
import os

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_USERNAME"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

def generate_verification_token():
    return secrets.token_urlsafe(32)

async def send_verification_email(email: str, token: str):
    verification_link = f"http://127.0.0.1:8000/auth/verify/{token}"
    
    message = MessageSchema(
        subject="Verify your Fraud Detection account",
        recipients=[email],
        body=f"""
        Hello,
        
        Please verify your email by clicking this link:
        {verification_link}
        
        This link expires in 24 hours.
        """,
        subtype="plain"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)