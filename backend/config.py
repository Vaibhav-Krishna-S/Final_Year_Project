"""
Configuration settings for the application
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load .env from the project root (one level up from backend/)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class Settings:
    def __init__(self):
        # Load from environment variables
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./engagement.db")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.LMS_API_KEY = os.getenv("LMS_API_KEY", "demo_key")
        
        # Security
        self.SECRET_KEY = os.getenv("SECRET_KEY", "demo-secret-key")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        # Application
        self.DEBUG = True
        self.HOST = "0.0.0.0"
        self.PORT = 8000
        self.FRONTEND_URL = "http://localhost:3000"
        
        # LMS Integration
        self.LMS_TYPE = os.getenv("LMS_TYPE", "mock")
        self.LMS_BASE_URL = os.getenv("LMS_BASE_URL")
        self.LMS_CLIENT_ID = os.getenv("LMS_CLIENT_ID")
        self.LMS_CLIENT_SECRET = os.getenv("LMS_CLIENT_SECRET")
        
        # AI Model Settings
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
        self.FACE_DETECTION_CONFIDENCE = 0.7
        self.EMOTION_DETECTION_CONFIDENCE = 0.6
        self.ENGAGEMENT_THRESHOLD = 0.5
        
        # Engagement Scoring Weights
        self.WEIGHT_EYE_CONTACT = 0.3
        self.WEIGHT_EMOTION = 0.25
        self.WEIGHT_PRESENCE = 0.25
        self.WEIGHT_POSTURE = 0.2

settings = Settings()