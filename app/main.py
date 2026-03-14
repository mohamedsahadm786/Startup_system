from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.database import engine
from app import models

# Load environment variables from .env file
load_dotenv()

# This line reads all the models we defined and creates the actual
# tables in the SQLite database file (app.db)
# If tables already exist, it skips them — safe to run multiple times
models.Base.metadata.create_all(bind=engine)

# Create the FastAPI application
app = FastAPI(
    title="Startup Ecosystem Platform",
    description="A platform for founders, investors, startups and developers.",
    version="1.0.0"
)

# CORS middleware — allows the frontend HTML pages to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Startup Ecosystem Platform is running"}
