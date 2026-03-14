from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.database import engine
from app import models
from app.routers import auth, startups

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Startup Ecosystem Platform",
    description="A platform for founders, investors, startups and developers.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(startups.router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Startup Ecosystem Platform is running"}