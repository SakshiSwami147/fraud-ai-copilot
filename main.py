from fastapi import FastAPI
from app.database import Base, engine
from app.api.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@app.get("/")
def home():
    return {"message": "Fraud Detection API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}