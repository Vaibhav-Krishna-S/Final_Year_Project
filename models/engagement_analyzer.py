"""
Main engagement analysis module combining face detection, gaze estimation, and emotion recognition
"""
import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, Any, Tuple, Optional
import logging

from .face_detector import FaceDetector
from .gaze_estimator import GazeEstimator
from .emotion_detector import EmotionDetector
from backend.config import settings

logger = logging.getLogger(__name__)

class EngagementAnalyzer:
    """Main class for analyzing student engagement from video frames"""
    
    def __init__(self):
        self.face_detector = FaceDetector()
        self.gaze_estimator = GazeEstimator()
        self.emotion_detector = EmotionDetector()
        
        # Engagement scoring weights
        self.weights = {
            'eye_contact': settings.WEIGHT_EYE_CONTACT,
            'emotion': settings.WEIGHT_EMOTION,
            'presence': settings.WEIGHT_PRESENCE,
            'posture': settings.WEIGHT_POSTURE
        }
    
    def analyze_frame(self, frame: np.ndarray, student_id: str = "unknown") -> Dict[str, Any]:
        """
        Analyze a single frame for engagement metrics
        
        Args:
            frame: Input video frame
            student_id: Identifier for the student
            
        Returns:
            Dictionary containing engagement analysis results
        """
        try:
            # Initialize result structure
            result = {
                'student_id': student_id,
                'session_id': 'default',
                'face_detected': False,
                'gaze_score': 0.0,
                'emotion_score': 0.0,
                'presence_score': 0.0,
                'posture_score': 0.0,
                'engagement_score': 0.0,
                'dominant_emotion': 'neutral',
                'gaze_direction': 'unknown'
            }
            
            # Step 1: Face Detection
            faces = self.face_detector.detect_faces(frame)
            
            if not faces:
                result['presence_score'] = 0.0
                return result
            
            result['face_detected'] = True
            result['presence_score'] = 1.0
            
            # Use the first detected face
            face = faces[0]
            face_region = self._extract_face_region(frame, face)
            
            # Step 2: Gaze Estimation
            gaze_result = self.gaze_estimator.estimate_gaze(frame, face)
            result['gaze_score'] = gaze_result['attention_score']
            result['gaze_direction'] = gaze_result['direction']
            
            # Step 3: Emotion Recognition
            emotion_result = self.emotion_detector.detect_emotion(face_region)
            result['emotion_score'] = emotion_result['engagement_score']
            result['dominant_emotion'] = emotion_result['dominant_emotion']
            
            # Step 4: Posture Analysis (simplified)
            result['posture_score'] = self._analyze_posture(frame, face)
            
            # Step 5: Calculate Overall Engagement Score
            result['engagement_score'] = self._calculate_engagement_score(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing frame: {str(e)}")
            return result
    
    def _extract_face_region(self, frame: np.ndarray, face_coords: Dict) -> np.ndarray:
        """Extract face region from frame"""
        x, y, w, h = face_coords['bbox']
        return frame[y:y+h, x:x+w]
    
    def _analyze_posture(self, frame: np.ndarray, face_coords: Dict) -> float:
        """
        Simplified posture analysis based on face position and orientation
        In a full implementation, this would use pose estimation
        """
        try:
            # Simple heuristic: face should be in upper portion of frame
            frame_height = frame.shape[0]
            face_y = face_coords['bbox'][1]
            
            # Good posture if face is in upper 60% of frame
            if face_y < frame_height * 0.6:
                return 0.8
            else:
                return 0.4
                
        except Exception:
            return 0.5
    
    def _calculate_engagement_score(self, metrics: Dict[str, Any]) -> float:
        """
        Calculate overall engagement score using weighted combination
        
        Formula: EI = w1*eye_contact + w2*emotion_score + w3*presence + w4*posture
        """
        try:
            score = (
                self.weights['eye_contact'] * metrics['gaze_score'] +
                self.weights['emotion'] * metrics['emotion_score'] +
                self.weights['presence'] * metrics['presence_score'] +
                self.weights['posture'] * metrics['posture_score']
            )
            
            # Normalize to 0-1 range
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {str(e)}")
            return 0.0
    
    def analyze_batch(self, frames: list, student_ids: list = None) -> list:
        """Analyze multiple frames in batch"""
        results = []
        
        for i, frame in enumerate(frames):
            student_id = student_ids[i] if student_ids else f"student_{i}"
            result = self.analyze_frame(frame, student_id)
            results.append(result)
        
        return results
    
    def get_session_summary(self, results: list) -> Dict[str, Any]:
        """Generate summary statistics for a session"""
        if not results:
            return {}
        
        engagement_scores = [r['engagement_score'] for r in results if r['face_detected']]
        
        if not engagement_scores:
            return {'message': 'No valid engagement data'}
        
        return {
            'average_engagement': np.mean(engagement_scores),
            'max_engagement': np.max(engagement_scores),
            'min_engagement': np.min(engagement_scores),
            'std_engagement': np.std(engagement_scores),
            'total_frames': len(results),
            'frames_with_face': len(engagement_scores),
            'attention_rate': len(engagement_scores) / len(results)
        }