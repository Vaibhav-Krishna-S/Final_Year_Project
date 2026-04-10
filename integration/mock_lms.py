"""
Mock LMS simulator for testing without real API keys
"""
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid

class MockLMSConnector:
    """Mock LMS connector for simulation"""
    
    def __init__(self):
        self.courses = [
            {'id': 'CS101', 'name': 'Introduction to Computer Science', 'code': 'CS101'},
            {'id': 'CS201', 'name': 'Data Structures', 'code': 'CS201'},
            {'id': 'CS301', 'name': 'Machine Learning', 'code': 'CS301'}
        ]
        
        self.students = [
            {'id': f'STUDENT_{i:03d}', 'name': f'Student {i}', 'email': f'student{i}@university.edu'}
            for i in range(1, 26)
        ]
        
        self.assignments = {}
        self.grades = {}
    
    def get_courses(self) -> List[Dict[str, Any]]:
        return self.courses
    
    def get_students(self, course_id: str) -> List[Dict[str, Any]]:
        return random.sample(self.students, 20)
    
    def create_assignment(self, course_id: str, assignment_data: Dict[str, Any]) -> Dict[str, Any]:
        assignment_id = str(uuid.uuid4())
        assignment = {
            'id': assignment_id,
            'name': assignment_data['name'],
            'points_possible': assignment_data.get('points', 100)
        }
        self.assignments[assignment_id] = assignment
        return assignment
    
    def submit_grades(self, course_id: str, assignment_id: str, grades: List[Dict[str, Any]]) -> bool:
        for grade in grades:
            self.grades[f"{assignment_id}_{grade['student_id']}"] = grade
        return True
    
    def generate_session_data(self, course_id: str) -> Dict[str, Any]:
        students = self.get_students(course_id)
        return {
            'session_id': f'SESSION_{uuid.uuid4().hex[:8]}',
            'course_id': course_id,
            'session_name': f'Demo Session - {datetime.now().strftime("%H:%M")}',
            'date': datetime.now().isoformat(),
            'student_scores': {s['id']: random.uniform(0.4, 0.9) for s in students}
        }

mock_lms = MockLMSConnector()