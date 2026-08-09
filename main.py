from fastapi import FastAPI
from app.database import Base, engine
from app.api.auth import router as auth_router
from app.api.password import router as password_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(password_router, prefix="/auth", tags=["Password"])

@app.get("/")
def home():
    return {"message": "Fraud Detection API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}