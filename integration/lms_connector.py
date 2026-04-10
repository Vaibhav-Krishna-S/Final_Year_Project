"""
LMS Integration module for connecting with various Learning Management Systems
"""
import requests
import json
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import logging
from datetime import datetime

from backend.config import settings
from .mock_lms import mock_lms

logger = logging.getLogger(__name__)

class LMSConnector(ABC):
    """Abstract base class for LMS connectors"""
    
    def __init__(self, base_url: str, api_key: str, client_id: str = None, client_secret: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = requests.Session()
        self._setup_authentication()
    
    @abstractmethod
    def _setup_authentication(self):
        """Setup authentication for the LMS"""
        pass
    
    @abstractmethod
    def get_courses(self) -> List[Dict[str, Any]]:
        """Get list of courses"""
        pass
    
    @abstractmethod
    def get_students(self, course_id: str) -> List[Dict[str, Any]]:
        """Get students enrolled in a course"""
        pass
    
    @abstractmethod
    def create_assignment(self, course_id: str, assignment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an assignment/activity"""
        pass
    
    @abstractmethod
    def submit_grades(self, course_id: str, assignment_id: str, grades: List[Dict[str, Any]]) -> bool:
        """Submit grades for an assignment"""
        pass

class CanvasConnector(LMSConnector):
    """Canvas LMS connector"""
    
    def _setup_authentication(self):
        """Setup Canvas API authentication"""
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
    
    def get_courses(self) -> List[Dict[str, Any]]:
        """Get Canvas courses"""
        try:
            response = self.session.get(f'{self.base_url}/api/v1/courses')
            response.raise_for_status()
            
            courses = []
            for course in response.json():
                courses.append({
                    'id': str(course['id']),
                    'name': course['name'],
                    'code': course.get('course_code', ''),
                    'enrollment_term': course.get('enrollment_term_id'),
                    'start_date': course.get('start_at'),
                    'end_date': course.get('end_at')
                })
            
            return courses
            
        except Exception as e:
            logger.error(f"Error fetching Canvas courses: {str(e)}")
            return []
    
    def get_students(self, course_id: str) -> List[Dict[str, Any]]:
        """Get Canvas course students"""
        try:
            response = self.session.get(
                f'{self.base_url}/api/v1/courses/{course_id}/enrollments',
                params={'type[]': 'StudentEnrollment', 'state[]': 'active'}
            )
            response.raise_for_status()
            
            students = []
            for enrollment in response.json():
                user = enrollment['user']
                students.append({
                    'id': str(user['id']),
                    'name': user['name'],
                    'email': user.get('email', ''),
                    'sis_user_id': user.get('sis_user_id'),
                    'enrollment_state': enrollment['enrollment_state']
                })
            
            return students
            
        except Exception as e:
            logger.error(f"Error fetching Canvas students: {str(e)}")
            return []
    
    def create_assignment(self, course_id: str, assignment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Canvas assignment"""
        try:
            payload = {
                'assignment': {
                    'name': assignment_data['name'],
                    'description': assignment_data.get('description', ''),
                    'points_possible': assignment_data.get('points', 100),
                    'grading_type': 'points',
                    'submission_types': ['none'],  # No submission required for engagement scores
                    'published': True
                }
            }
            
            response = self.session.post(
                f'{self.base_url}/api/v1/courses/{course_id}/assignments',
                json=payload
            )
            response.raise_for_status()
            
            assignment = response.json()
            return {
                'id': str(assignment['id']),
                'name': assignment['name'],
                'points_possible': assignment['points_possible'],
                'html_url': assignment['html_url']
            }
            
        except Exception as e:
            logger.error(f"Error creating Canvas assignment: {str(e)}")
            return {}
    
    def submit_grades(self, course_id: str, assignment_id: str, grades: List[Dict[str, Any]]) -> bool:
        """Submit grades to Canvas"""
        try:
            for grade in grades:
                payload = {
                    'submission': {
                        'posted_grade': grade['score']
                    }
                }
                
                response = self.session.put(
                    f'{self.base_url}/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{grade["student_id"]}',
                    json=payload
                )
                response.raise_for_status()
            
            return True
            
        except Exception as e:
            logger.error(f"Error submitting Canvas grades: {str(e)}")
            return False

class MoodleConnector(LMSConnector):
    """Moodle LMS connector"""
    
    def _setup_authentication(self):
        """Setup Moodle web service authentication"""
        self.session.params.update({
            'wstoken': self.api_key,
            'moodlewsrestformat': 'json'
        })
    
    def _call_webservice(self, function: str, params: Dict[str, Any] = None) -> Any:
        """Call Moodle web service function"""
        try:
            data = {
                'wsfunction': function,
                **(params or {})
            }
            
            response = self.session.post(f'{self.base_url}/webservice/rest/server.php', data=data)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, dict) and 'exception' in result:
                raise Exception(f"Moodle API error: {result['message']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Moodle web service error: {str(e)}")
            raise
    
    def get_courses(self) -> List[Dict[str, Any]]:
        """Get Moodle courses"""
        try:
            courses_data = self._call_webservice('core_enrol_get_users_courses', {'userid': 'self'})
            
            courses = []
            for course in courses_data:
                courses.append({
                    'id': str(course['id']),
                    'name': course['fullname'],
                    'code': course['shortname'],
                    'category': course.get('categoryname', ''),
                    'start_date': datetime.fromtimestamp(course['startdate']).isoformat() if course.get('startdate') else None,
                    'end_date': datetime.fromtimestamp(course['enddate']).isoformat() if course.get('enddate') else None
                })
            
            return courses
            
        except Exception as e:
            logger.error(f"Error fetching Moodle courses: {str(e)}")
            return []
    
    def get_students(self, course_id: str) -> List[Dict[str, Any]]:
        """Get Moodle course students"""
        try:
            students_data = self._call_webservice(
                'core_enrol_get_enrolled_users',
                {'courseid': course_id}
            )
            
            students = []
            for user in students_data:
                # Filter only students (not teachers/admins)
                if any(role['shortname'] == 'student' for role in user.get('roles', [])):
                    students.append({
                        'id': str(user['id']),
                        'name': f"{user['firstname']} {user['lastname']}",
                        'email': user.get('email', ''),
                        'username': user.get('username', ''),
                        'last_access': datetime.fromtimestamp(user['lastaccess']).isoformat() if user.get('lastaccess') else None
                    })
            
            return students
            
        except Exception as e:
            logger.error(f"Error fetching Moodle students: {str(e)}")
            return []
    
    def create_assignment(self, course_id: str, assignment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Moodle assignment"""
        try:
            # Moodle assignment creation is more complex and requires specific module setup
            # This is a simplified version
            assignment_params = {
                'courseid': course_id,
                'assignments': [{
                    'name': assignment_data['name'],
                    'intro': assignment_data.get('description', ''),
                    'grade': assignment_data.get('points', 100),
                    'duedate': int(datetime.now().timestamp()) + 86400 * 7  # 1 week from now
                }]
            }
            
            result = self._call_webservice('mod_assign_add_assignments', assignment_params)
            
            if result and len(result) > 0:
                assignment = result[0]
                return {
                    'id': str(assignment['id']),
                    'name': assignment['name'],
                    'course_module_id': assignment['cmid']
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error creating Moodle assignment: {str(e)}")
            return {}
    
    def submit_grades(self, course_id: str, assignment_id: str, grades: List[Dict[str, Any]]) -> bool:
        """Submit grades to Moodle"""
        try:
            grade_params = {
                'assignmentid': assignment_id,
                'grades': [
                    {
                        'userid': grade['student_id'],
                        'grade': grade['score']
                    }
                    for grade in grades
                ]
            }
            
            self._call_webservice('mod_assign_save_grades', grade_params)
            return True
            
        except Exception as e:
            logger.error(f"Error submitting Moodle grades: {str(e)}")
            return False

class LMSIntegrationManager:
    """Manager class for LMS integrations"""
    
    def __init__(self):
        self.connectors = {}
        self._initialize_connectors()
    
    def _initialize_connectors(self):
        """Initialize LMS connectors based on configuration"""
        if settings.LMS_TYPE and settings.LMS_TYPE.lower() == 'mock':
            self.connectors['mock'] = mock_lms
            logger.info("Initialized mock LMS connector")
        elif settings.LMS_TYPE and settings.LMS_BASE_URL and settings.LMS_API_KEY:
            try:
                if settings.LMS_TYPE.lower() == 'canvas':
                    self.connectors['canvas'] = CanvasConnector(
                        settings.LMS_BASE_URL,
                        settings.LMS_API_KEY,
                        settings.LMS_CLIENT_ID,
                        settings.LMS_CLIENT_SECRET
                    )
                elif settings.LMS_TYPE.lower() == 'moodle':
                    self.connectors['moodle'] = MoodleConnector(
                        settings.LMS_BASE_URL,
                        settings.LMS_API_KEY
                    )
                
                logger.info(f"Initialized {settings.LMS_TYPE} connector")
                
            except Exception as e:
                logger.error(f"Failed to initialize LMS connector: {str(e)}")
        else:
            # Fallback to mock if no valid configuration
            self.connectors['mock'] = mock_lms
            logger.info("Using mock LMS connector (no valid LMS configuration found)")
    
    def get_connector(self, lms_type: str = None):
        """Get LMS connector by type"""
        lms_type = lms_type or getattr(settings, 'LMS_TYPE', 'mock').lower()
        return self.connectors.get(lms_type, mock_lms)
    
    def sync_engagement_scores(self, course_id: str, session_data: Dict[str, Any]) -> bool:
        """Sync engagement scores to LMS as assignment grades"""
        try:
            connector = self.get_connector() or mock_lms
            
            # Create engagement assignment
            assignment_data = {
                'name': f"Engagement Score - {session_data['session_name']}",
                'description': f"Automated engagement analysis for session on {session_data['date']}",
                'points': 100
            }
            
            assignment = connector.create_assignment(course_id, assignment_data)
            if not assignment:
                logger.error("Failed to create engagement assignment")
                return False
            
            # Prepare grades (convert engagement scores to 0-100 scale)
            grades = []
            for student_id, engagement_score in session_data['student_scores'].items():
                grades.append({
                    'student_id': student_id,
                    'score': round(engagement_score * 100, 2)
                })
            
            # Submit grades
            success = connector.submit_grades(course_id, assignment['id'], grades)
            
            if success:
                logger.info(f"Successfully synced engagement scores for {len(grades)} students")
            
            return success
            
        except Exception as e:
            logger.error(f"Error syncing engagement scores: {str(e)}")
            return False

# Global integration manager
lms_manager = LMSIntegrationManager()