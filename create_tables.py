"""
Create database tables
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import create_tables, db_manager
from database.models import Student, Session
from datetime import datetime

def setup_database():
    print("Creating database tables...")
    
    try:
        # Create all tables
        create_tables()
        print("✅ Tables created successfully")
        
        # Add sample data
        from database.connection import get_db_context
        with get_db_context() as db:
            # Sample student
            student = Student(
                id="STUDENT_001",
                name="Demo Student",
                email="demo@university.edu"
            )
            db.merge(student)
            
            # Sample session
            session = Session(
                id="SESSION_001",
                course_id="CS101",
                course_name="Introduction to Computer Science",
                instructor_id="instructor_001",
                session_name="Demo Session",
                start_time=datetime.now(),
                status="active"
            )
            db.merge(session)
            
        print("✅ Sample data added")
        print("🚀 Database ready!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    setup_database()