"""
Minimal test to check if basic components work
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    try:
        print("Testing imports...")
        
        # Test basic imports
        import cv2
        print("✅ OpenCV imported")
        
        import mediapipe as mp
        print("✅ MediaPipe imported")
        
        import numpy as np
        print("✅ NumPy imported")
        
        # Test database
        from database.connection import db_manager
        print("✅ Database connection imported")
        
        # Test config
        from backend.config import settings
        print("✅ Settings imported")
        
        # Test Gemini
        from models.gemini_analyzer import gemini_analyzer
        print("✅ Gemini analyzer imported")
        
        print("\n🎉 All core components working!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    try:
        from database.connection import db_manager
        if db_manager.check_connection():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    print("=== Student Engagement System Test ===\n")
    
    imports_ok = test_imports()
    if imports_ok:
        db_ok = test_database()
        
        if db_ok:
            print("\n🚀 System ready to run!")
            print("Next: python backend/main.py")
        else:
            print("\n⚠️ Check database configuration")
    else:
        print("\n⚠️ Install missing dependencies first")