"""
Check database connection and data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_db_context
from database.models import Student, Session, EngagementRecord
from backend.config import settings

def check_database():
    print(f"Database URL: {settings.DATABASE_URL}")
    print("Checking database connection...")
    
    try:
        with get_db_context() as db:
            # Check tables exist
            students = db.query(Student).count()
            sessions = db.query(Session).count()
            records = db.query(EngagementRecord).count()
            
            print(f"✅ Students: {students}")
            print(f"✅ Sessions: {sessions}")
            print(f"✅ Engagement Records: {records}")
            
            if records == 0:
                print("⚠️ No engagement data found - dashboard will be empty")
                print("Run: python add_sample_data.py")
            else:
                print("✅ Data available for dashboard")
                
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_database()