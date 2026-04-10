"""
Database models for Student Engagement Analysis
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Student(Base):
    """Student model"""
    __tablename__ = "students"
    
    id = Column(String, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    lms_id = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    engagement_records = relationship("EngagementRecord", back_populates="student")

class Session(Base):
    """Class session model"""
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True)
    course_id = Column(String(100), nullable=False)
    course_name = Column(String(200))
    instructor_id = Column(String(100))
    session_name = Column(String(200))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    status = Column(String(20), default="active")  # active, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    engagement_records = relationship("EngagementRecord", back_populates="session")

class EngagementRecord(Base):
    """Individual engagement measurement record"""
    __tablename__ = "engagement_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Engagement metrics
    engagement_score = Column(Float, nullable=False)
    face_detected = Column(Boolean, default=False)
    gaze_score = Column(Float, default=0.0)
    emotion_score = Column(Float, default=0.0)
    presence_score = Column(Float, default=0.0)
    posture_score = Column(Float, default=0.0)
    
    # Additional metadata
    dominant_emotion = Column(String(20))
    gaze_direction = Column(String(20))
    confidence_level = Column(Float, default=0.0)
    
    # Relationships
    student = relationship("Student", back_populates="engagement_records")
    session = relationship("Session", back_populates="engagement_records")

class EngagementSummary(Base):
    """Aggregated engagement summary per student per session"""
    __tablename__ = "engagement_summaries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    
    # Summary metrics
    average_engagement = Column(Float, nullable=False)
    max_engagement = Column(Float, nullable=False)
    min_engagement = Column(Float, nullable=False)
    std_engagement = Column(Float, nullable=False)
    
    # Participation metrics
    total_frames = Column(Integer, default=0)
    frames_with_face = Column(Integer, default=0)
    attention_rate = Column(Float, default=0.0)
    
    # Time metrics
    total_duration_minutes = Column(Float, default=0.0)
    active_duration_minutes = Column(Float, default=0.0)
    
    # Emotion analysis
    dominant_emotion = Column(String(20))
    emotion_distribution = Column(Text)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Alert(Base):
    """Engagement alerts and notifications"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    
    alert_type = Column(String(50), nullable=False)  # low_engagement, no_face_detected, etc.
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    message = Column(Text, nullable=False)
    
    # Alert metadata
    threshold_value = Column(Float)
    actual_value = Column(Float)
    duration_minutes = Column(Float)
    
    # Status
    status = Column(String(20), default="active")  # active, acknowledged, resolved
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)

class LMSIntegration(Base):
    """LMS integration configuration and logs"""
    __tablename__ = "lms_integrations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    lms_type = Column(String(50), nullable=False)  # canvas, moodle, google_classroom
    lms_instance_url = Column(String(500))
    
    # Configuration
    client_id = Column(String(200))
    is_active = Column(Boolean, default=True)
    
    # Sync status
    last_sync_at = Column(DateTime)
    sync_status = Column(String(20), default="pending")  # pending, success, failed
    sync_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)