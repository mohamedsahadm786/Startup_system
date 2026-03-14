from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create the FastAPI application
app = FastAPI(
    title="Startup Ecosystem Platform",
    description="A platform for founders, investors, startups and developers.",
    version="1.0.0"
)

# CORS middleware — allows the frontend (HTML pages) to talk to this backend
# Without this, the browser will block frontend API calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Allow all origins (fine for hackathon)
    allow_credentials=True,
    allow_methods=["*"],      # Allow GET, POST, PUT, DELETE
    allow_headers=["*"],      # Allow all headers including Authorization
)

# Health check endpoint — just to confirm the server is running
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Startup Ecosystem Platform is running"}