"""
Gaze estimation module using MediaPipe Face Mesh
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Any, Tuple

class GazeEstimator:
    """Gaze estimation using MediaPipe Face Mesh"""
    
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eye landmark indices for MediaPipe Face Mesh
        self.LEFT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        self.RIGHT_EYE_INDICES = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        
        # Iris landmarks
        self.LEFT_IRIS_INDICES = [474, 475, 476, 477]
        self.RIGHT_IRIS_INDICES = [469, 470, 471, 472]
    
    def estimate_gaze(self, frame: np.ndarray, face_coords: Dict = None) -> Dict[str, Any]:
        """
        Estimate gaze direction and attention score
        
        Args:
            frame: Input image frame
            face_coords: Face coordinates (optional, for optimization)
            
        Returns:
            Dictionary containing gaze analysis results
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.face_mesh.process(rgb_frame)
        
        gaze_result = {
            'attention_score': 0.0,
            'direction': 'unknown',
            'left_eye_ratio': 0.0,
            'right_eye_ratio': 0.0,
            'iris_positions': None
        }
        
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]
            
            # Extract eye regions
            left_eye_points = self._get_eye_landmarks(landmarks, self.LEFT_EYE_INDICES, frame.shape)
            right_eye_points = self._get_eye_landmarks(landmarks, self.RIGHT_EYE_INDICES, frame.shape)
            
            # Extract iris positions
            left_iris = self._get_eye_landmarks(landmarks, self.LEFT_IRIS_INDICES, frame.shape)
            right_iris = self._get_eye_landmarks(landmarks, self.RIGHT_IRIS_INDICES, frame.shape)
            
            # Calculate gaze ratios
            left_ratio = self._calculate_gaze_ratio(left_eye_points, left_iris)
            right_ratio = self._calculate_gaze_ratio(right_eye_points, right_iris)
            
            gaze_result['left_eye_ratio'] = left_ratio
            gaze_result['right_eye_ratio'] = right_ratio
            
            # Determine gaze direction
            avg_ratio = (left_ratio + right_ratio) / 2
            gaze_result['direction'] = self._classify_gaze_direction(avg_ratio)
            
            # Calculate attention score (higher when looking at camera)
            gaze_result['attention_score'] = self._calculate_attention_score(avg_ratio)
            
            # Store iris positions for visualization
            gaze_result['iris_positions'] = {
                'left': left_iris,
                'right': right_iris
            }
        
        return gaze_result
    
    def _get_eye_landmarks(self, landmarks, indices: list, frame_shape: tuple) -> np.ndarray:
        """Extract eye landmark coordinates"""
        h, w = frame_shape[:2]
        points = []
        
        for idx in indices:
            landmark = landmarks.landmark[idx]
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            points.append([x, y])
        
        return np.array(points)
    
    def _calculate_gaze_ratio(self, eye_points: np.ndarray, iris_points: np.ndarray) -> float:
        """
        Calculate gaze ratio based on iris position relative to eye corners
        """
        if len(eye_points) == 0 or len(iris_points) == 0:
            return 0.5
        
        # Get eye corners (leftmost and rightmost points)
        left_corner = eye_points[np.argmin(eye_points[:, 0])]
        right_corner = eye_points[np.argmax(eye_points[:, 0])]
        
        # Get iris center
        iris_center = np.mean(iris_points, axis=0)
        
        # Calculate ratio (0 = looking left, 1 = looking right, 0.5 = center)
        eye_width = right_corner[0] - left_corner[0]
        if eye_width == 0:
            return 0.5
        
        iris_position = (iris_center[0] - left_corner[0]) / eye_width
        return np.clip(iris_position, 0.0, 1.0)
    
    def _classify_gaze_direction(self, ratio: float) -> str:
        """Classify gaze direction based on ratio"""
        if ratio < 0.35:
            return 'left'
        elif ratio > 0.65:
            return 'right'
        else:
            return 'center'
    
    def _calculate_attention_score(self, ratio: float) -> float:
        """
        Calculate attention score (0-1) based on gaze direction
        Higher score when looking at center (camera)
        """
        # Gaussian-like function centered at 0.5
        center_distance = abs(ratio - 0.5)
        attention_score = np.exp(-8 * center_distance**2)
        return float(attention_score)
    
    def draw_gaze_analysis(self, frame: np.ndarray, gaze_result: Dict[str, Any]) -> np.ndarray:
        """Draw gaze analysis results on frame"""
        annotated_frame = frame.copy()
        
        # Draw attention score
        score_text = f"Attention: {gaze_result['attention_score']:.2f}"
        cv2.putText(
            annotated_frame,
            score_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )
        
        # Draw gaze direction
        direction_text = f"Gaze: {gaze_result['direction']}"
        cv2.putText(
            annotated_frame,
            direction_text,
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )
        
        # Draw iris positions if available
        if gaze_result['iris_positions']:
            for eye, iris_points in gaze_result['iris_positions'].items():
                if iris_points is not None and len(iris_points) > 0:
                    center = np.mean(iris_points, axis=0).astype(int)
                    cv2.circle(annotated_frame, tuple(center), 3, (255, 0, 0), -1)
        
        return annotated_frame