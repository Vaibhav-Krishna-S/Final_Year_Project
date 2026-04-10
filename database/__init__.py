"""
Database package for Student Engagement Analysis
"""

from .models import (
    Base,
    Student,
    Session,
    EngagementRecord,
    EngagementSummary,
    Alert,
    LMSIntegration
)
from .connection import (
    engine,
    SessionLocal,
    get_db_session,
    get_db_context,
    db_manager,
    create_tables
)

__all__ = [
    'Base',
    'Student',
    'Session', 
    'EngagementRecord',
    'EngagementSummary',
    'Alert',
    'LMSIntegration',
    'engine',
    'SessionLocal',
    'get_db_session',
    'get_db_context',
    'db_manager',
    'create_tables'
]