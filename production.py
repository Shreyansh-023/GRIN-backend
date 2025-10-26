import os
from pathlib import Path

# Production settings
PROD_ENV = os.getenv("RENDER", "0") == "1"
DEBUG = not PROD_ENV

# Paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
USER_IMAGES_DIR = STATIC_DIR / "user_images"
ACCEPTED_DIR = STATIC_DIR / "accepted"
REPORTS_DIR = STATIC_DIR / "reports"

# Ensure directories exist
USER_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
ACCEPTED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Model settings
MODEL_TIMEOUT = 300  # seconds

# CORS settings
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://lumera-frontend.onrender.com",  # Add your frontend URL here
]

# Initialize production settings
def init_production():
    """Initialize production-specific settings"""
    if PROD_ENV:
        print("🚀 Running in production mode")
        # Add any production-specific initialization here
    else:
        print("🔧 Running in development mode")