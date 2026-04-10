"""
Face detection module using MediaPipe
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import List, Dict, Any

class FaceDetector:
    """Face detection using MediaPipe Face Detection"""
    
    def __init__(self, confidence_threshold: float = 0.7):
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=confidence_threshold
        )
    
    def detect_faces(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect faces in the given frame
        
        Args:
            frame: Input image frame
            
        Returns:
            List of detected faces with bounding boxes and landmarks
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.face_detection.process(rgb_frame)
        
        faces = []
        
        if results.detections:
            for detection in results.detections:
                # Get bounding box
                bbox = detection.location_data.relative_bounding_box
                h, w, _ = frame.shape
                
                # Convert relative coordinates to absolute
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                # Get key points
                keypoints = []
                if detection.location_data.relative_keypoints:
                    for keypoint in detection.location_data.relative_keypoints:
                        kp_x = int(keypoint.x * w)
                        kp_y = int(keypoint.y * h)
                        keypoints.append((kp_x, kp_y))
                
                face_data = {
                    'bbox': (x, y, width, height),
                    'confidence': detection.score[0],
                    'keypoints': keypoints,
                    'center': (x + width // 2, y + height // 2)
                }
                
                faces.append(face_data)
        
        return faces
    
    def draw_detections(self, frame: np.ndarray, faces: List[Dict[str, Any]]) -> np.ndarray:
        """
        Draw face detection results on the frame
        
        Args:
            frame: Input image frame
            faces: List of detected faces
            
        Returns:
            Frame with drawn detections
        """
        annotated_frame = frame.copy()
        
        for face in faces:
            x, y, w, h = face['bbox']
            confidence = face['confidence']
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw confidence score
            cv2.putText(
                annotated_frame,
                f'Face: {confidence:.2f}',
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )
            
            # Draw keypoints if available
            for kp in face['keypoints']:
                cv2.circle(annotated_frame, kp, 3, (255, 0, 0), -1)
        
        return annotated_frame
    
    def get_largest_face(self, faces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get the largest detected face (closest to camera)"""
        if not faces:
            return None
        
        largest_face = max(faces, key=lambda f: f['bbox'][2] * f['bbox'][3])
        return largest_face
    
    def is_face_centered(self, face: Dict[str, Any], frame_shape: tuple, threshold: float = 0.3) -> bool:
        """Check if face is reasonably centered in the frame"""
        frame_h, frame_w = frame_shape[:2]
        face_center_x, face_center_y = face['center']
        
        frame_center_x = frame_w // 2
        frame_center_y = frame_h // 2
        
        # Calculate relative distance from center
        dist_x = abs(face_center_x - frame_center_x) / frame_w
        dist_y = abs(face_center_y - frame_center_y) / frame_h
        
        return dist_x < threshold and dist_y < threshold