"""
Unit tests for engagement analyzer
"""
import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.engagement_analyzer import EngagementAnalyzer
from models.face_detector import FaceDetector
from models.gaze_estimator import GazeEstimator
from models.emotion_detector import EmotionDetector

class TestEngagementAnalyzer:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = EngagementAnalyzer()
        
        # Create a test image (simple colored rectangle)
        self.test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.test_frame[:, :] = [100, 150, 200]  # BGR color
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        assert isinstance(self.analyzer.face_detector, FaceDetector)
        assert isinstance(self.analyzer.gaze_estimator, GazeEstimator)
        assert isinstance(self.analyzer.emotion_detector, EmotionDetector)
        assert self.analyzer.weights['eye_contact'] > 0
        assert self.analyzer.weights['emotion'] > 0
        assert self.analyzer.weights['presence'] > 0
        assert self.analyzer.weights['posture'] > 0
    
    @patch('models.face_detector.FaceDetector.detect_faces')
    def test_analyze_frame_no_face(self, mock_detect_faces):
        """Test frame analysis when no face is detected"""
        mock_detect_faces.return_value = []
        
        result = self.analyzer.analyze_frame(self.test_frame)
        
        assert result['face_detected'] is False
        assert result['presence_score'] == 0.0
        assert result['engagement_score'] == 0.0
        assert result['student_id'] == 'unknown'
    
    @patch('models.face_detector.FaceDetector.detect_faces')
    @patch('models.gaze_estimator.GazeEstimator.estimate_gaze')
    @patch('models.emotion_detector.EmotionDetector.detect_emotion')
    def test_analyze_frame_with_face(self, mock_emotion, mock_gaze, mock_detect_faces):
        """Test frame analysis when face is detected"""
        # Mock face detection
        mock_detect_faces.return_value = [{
            'bbox': (100, 100, 200, 200),
            'confidence': 0.9,
            'keypoints': [],
            'center': (200, 200)
        }]
        
        # Mock gaze estimation
        mock_gaze.return_value = {
            'attention_score': 0.8,
            'direction': 'center',
            'left_eye_ratio': 0.5,
            'right_eye_ratio': 0.5
        }
        
        # Mock emotion detection
        mock_emotion.return_value = {
            'dominant_emotion': 'happy',
            'engagement_score': 0.9,
            'confidence': 0.8
        }
        
        result = self.analyzer.analyze_frame(self.test_frame, 'test_student')
        
        assert result['face_detected'] is True
        assert result['presence_score'] == 1.0
        assert result['student_id'] == 'test_student'
        assert result['gaze_score'] == 0.8
        assert result['emotion_score'] == 0.9
        assert result['dominant_emotion'] == 'happy'
        assert result['engagement_score'] > 0
    
    def test_calculate_engagement_score(self):
        """Test engagement score calculation"""
        metrics = {
            'gaze_score': 0.8,
            'emotion_score': 0.7,
            'presence_score': 1.0,
            'posture_score': 0.6
        }
        
        score = self.analyzer._calculate_engagement_score(metrics)
        
        assert 0 <= score <= 1
        assert isinstance(score, float)
    
    def test_analyze_batch(self):
        """Test batch analysis"""
        frames = [self.test_frame, self.test_frame]
        student_ids = ['student1', 'student2']
        
        with patch.object(self.analyzer, 'analyze_frame') as mock_analyze:
            mock_analyze.return_value = {'engagement_score': 0.5, 'face_detected': True}
            
            results = self.analyzer.analyze_batch(frames, student_ids)
            
            assert len(results) == 2
            assert mock_analyze.call_count == 2
    
    def test_get_session_summary(self):
        """Test session summary generation"""
        results = [
            {'engagement_score': 0.8, 'face_detected': True},
            {'engagement_score': 0.6, 'face_detected': True},
            {'engagement_score': 0.7, 'face_detected': False}
        ]
        
        summary = self.analyzer.get_session_summary(results)
        
        assert 'average_engagement' in summary
        assert 'max_engagement' in summary
        assert 'min_engagement' in summary
        assert 'total_frames' in summary
        assert summary['total_frames'] == 3
        assert summary['frames_with_face'] == 2

class TestFaceDetector:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.detector = FaceDetector()
        self.test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    def test_detector_initialization(self):
        """Test detector initialization"""
        assert self.detector.face_detection is not None
        assert hasattr(self.detector, 'mp_face_detection')
    
    @patch('mediapipe.solutions.face_detection.FaceDetection.process')
    def test_detect_faces_no_detection(self, mock_process):
        """Test face detection when no faces are found"""
        mock_process.return_value.detections = None
        
        faces = self.detector.detect_faces(self.test_frame)
        
        assert faces == []
    
    def test_get_largest_face(self):
        """Test getting largest face"""
        faces = [
            {'bbox': (0, 0, 100, 100)},  # Area: 10000
            {'bbox': (0, 0, 150, 150)},  # Area: 22500
            {'bbox': (0, 0, 80, 80)}     # Area: 6400
        ]
        
        largest = self.detector.get_largest_face(faces)
        
        assert largest['bbox'] == (0, 0, 150, 150)
    
    def test_get_largest_face_empty(self):
        """Test getting largest face with empty list"""
        largest = self.detector.get_largest_face([])
        assert largest is None

class TestGazeEstimator:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.estimator = GazeEstimator()
        self.test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    def test_estimator_initialization(self):
        """Test estimator initialization"""
        assert self.estimator.face_mesh is not None
        assert len(self.estimator.LEFT_EYE_INDICES) > 0
        assert len(self.estimator.RIGHT_EYE_INDICES) > 0
    
    def test_classify_gaze_direction(self):
        """Test gaze direction classification"""
        assert self.estimator._classify_gaze_direction(0.2) == 'left'
        assert self.estimator._classify_gaze_direction(0.5) == 'center'
        assert self.estimator._classify_gaze_direction(0.8) == 'right'
    
    def test_calculate_attention_score(self):
        """Test attention score calculation"""
        # Center gaze should have high attention
        center_score = self.estimator._calculate_attention_score(0.5)
        left_score = self.estimator._calculate_attention_score(0.1)
        
        assert center_score > left_score
        assert 0 <= center_score <= 1
        assert 0 <= left_score <= 1

class TestEmotionDetector:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.detector = EmotionDetector()
        self.test_face = np.zeros((48, 48, 3), dtype=np.uint8)
    
    def test_detector_initialization(self):
        """Test detector initialization"""
        assert 'happy' in self.detector.emotion_engagement_map
        assert 'sad' in self.detector.emotion_engagement_map
        assert self.detector.emotion_engagement_map['happy'] > self.detector.emotion_engagement_map['sad']
    
    def test_get_engagement_from_emotions(self):
        """Test engagement calculation from emotions"""
        emotions = {
            'happy': 0.7,
            'neutral': 0.2,
            'sad': 0.1
        }
        
        engagement = self.detector.get_engagement_from_emotions(emotions)
        
        assert 0 <= engagement <= 1
        assert isinstance(engagement, float)
    
    def test_is_positive_emotion(self):
        """Test positive emotion classification"""
        assert self.detector.is_positive_emotion('happy') is True
        assert self.detector.is_positive_emotion('neutral') is True
        assert self.detector.is_positive_emotion('sad') is False
        assert self.detector.is_positive_emotion('angry') is False
    
    def test_get_emotion_color(self):
        """Test emotion color mapping"""
        color = self.detector.get_emotion_color('happy')
        assert isinstance(color, tuple)
        assert len(color) == 3
        assert all(0 <= c <= 255 for c in color)

if __name__ == '__main__':
    pytest.main([__file__])