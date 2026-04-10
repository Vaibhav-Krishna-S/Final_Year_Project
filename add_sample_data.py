"""
Add sample engagement data for dashboard testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_db_context
from database.models import Student, Session, EngagementRecord
from datetime import datetime, timedelta
import random

def add_sample_data():
    print("Adding sample engagement data...")
    
    try:
        with get_db_context() as db:
            # Create sample student
            student = Student(
                id="STUDENT_001",
                name="Demo Student",
                email="demo@university.edu"
            )
            db.merge(student)
            
            # Create sample session
            session = Session(
                id="SESSION_001",
                course_id="CS101",
                course_name="Introduction to Computer Science",
                instructor_id="instructor_001",
                session_name="Demo Session",
                start_time=datetime.now() - timedelta(minutes=30),
                status="active"
            )
            db.merge(session)
            
            # Add sample engagement records
            base_time = datetime.now() - timedelta(minutes=30)
            
            for i in range(50):  # 50 data points
                record = EngagementRecord(
                    student_id="STUDENT_001",
                    session_id="SESSION_001",
                    timestamp=base_time + timedelta(seconds=i*30),
                    engagement_score=random.uniform(0.4, 0.9),
                    face_detected=random.choice([True, True, True, False]),  # 75% face detected
                    gaze_score=random.uniform(0.3, 0.8),
                    emotion_score=random.uniform(0.4, 0.9),
                    presence_score=1.0 if random.random() > 0.2 else 0.0,
                    posture_score=random.uniform(0.5, 0.8),
                    dominant_emotion=random.choice(['happy', 'neutral', 'focused', 'surprised']),
                    gaze_direction=random.choice(['center', 'left', 'right'])
                )
                db.add(record)
            
        print("✅ Sample data added successfully!")
        print("🔄 Refresh your dashboard at http://localhost:8050")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_sample_data()