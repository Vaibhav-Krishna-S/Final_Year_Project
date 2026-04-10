"""
Demo script for Student Engagement Analysis Tool
Simulates engagement analysis with webcam or sample video
"""
import cv2
import numpy as np
import time
import json
from datetime import datetime
import argparse
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.engagement_analyzer import EngagementAnalyzer
from database.connection import get_db_context, create_tables
from database.models import Student, Session, EngagementRecord

class EngagementDemo:
    """Demo class for engagement analysis"""
    
    def __init__(self, use_webcam=True, video_path=None):
        self.analyzer = EngagementAnalyzer()
        self.use_webcam = use_webcam
        self.video_path = video_path
        self.cap = None
        self.session_id = f"demo_session_{int(time.time())}"
        self.student_id = "demo_student"
        
        # Initialize database
        try:
            create_tables()
            self._create_demo_data()
        except Exception as e:
            print(f"Database initialization failed: {e}")
    
    def _create_demo_data(self):
        """Create demo student and session data"""
        try:
            with get_db_context() as db:
                # Create demo student
                student = Student(
                    id=self.student_id,
                    name="Demo Student",
                    email="demo@example.com"
                )
                db.merge(student)
                
                # Create demo session
                session = Session(
                    id=self.session_id,
                    course_id="DEMO_COURSE",
                    course_name="Demo Course",
                    instructor_id="demo_instructor",
                    session_name="Demo Session",
                    start_time=datetime.now(),
                    status="active"
                )
                db.merge(session)
                
        except Exception as e:
            print(f"Error creating demo data: {e}")
    
    def setup_video_capture(self):
        """Setup video capture from webcam or file"""
        try:
            if self.use_webcam:
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    print("Error: Could not open webcam")
                    return False
                print("Using webcam for demo")
            else:
                if not os.path.exists(self.video_path):
                    print(f"Error: Video file {self.video_path} not found")
                    return False
                self.cap = cv2.VideoCapture(self.video_path)
                print(f"Using video file: {self.video_path}")
            
            return True
            
        except Exception as e:
            print(f"Error setting up video capture: {e}")
            return False
    
    def run_analysis(self, duration_seconds=60):
        """Run engagement analysis demo"""
        if not self.setup_video_capture():
            return
        
        print(f"\nStarting engagement analysis demo...")
        print(f"Duration: {duration_seconds} seconds")
        print("Press 'q' to quit early\n")
        
        start_time = time.time()
        frame_count = 0
        engagement_history = []
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    if self.use_webcam:
                        print("Error reading from webcam")
                        break
                    else:
                        # Loop video for demo
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                
                # Analyze engagement every 2 seconds
                current_time = time.time()
                if current_time - start_time >= frame_count * 2:
                    
                    # Analyze frame
                    result = self.analyzer.analyze_frame(frame, self.student_id)
                    result['session_id'] = self.session_id
                    
                    # Store in database
                    self._store_engagement_record(result)
                    
                    # Add to history
                    engagement_history.append(result)
                    
                    # Print results
                    self._print_analysis_result(result, frame_count)
                    
                    frame_count += 1
                
                # Draw analysis overlay
                annotated_frame = self._draw_analysis_overlay(frame, result if 'result' in locals() else None)
                
                # Display frame
                cv2.imshow('Engagement Analysis Demo', annotated_frame)
                
                # Check for quit or time limit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nDemo stopped by user")
                    break
                
                if current_time - start_time >= duration_seconds:
                    print(f"\nDemo completed ({duration_seconds} seconds)")
                    break
        
        except KeyboardInterrupt:
            print("\nDemo interrupted by user")
        
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            
            # Print summary
            self._print_summary(engagement_history)
    
    def _store_engagement_record(self, result):
        """Store engagement record in database"""
        try:
            with get_db_context() as db:
                record = EngagementRecord(
                    student_id=result['student_id'],
                    session_id=result['session_id'],
                    engagement_score=result['engagement_score'],
                    face_detected=result['face_detected'],
                    gaze_score=result['gaze_score'],
                    emotion_score=result['emotion_score'],
                    presence_score=result['presence_score'],
                    posture_score=result['posture_score'],
                    dominant_emotion=result['dominant_emotion'],
                    gaze_direction=result['gaze_direction']
                )
                db.add(record)
                
        except Exception as e:
            print(f"Error storing record: {e}")
    
    def _print_analysis_result(self, result, frame_num):
        """Print analysis result to console"""
        print(f"Frame {frame_num:3d} | "
              f"Engagement: {result['engagement_score']:.2f} | "
              f"Face: {'✓' if result['face_detected'] else '✗'} | "
              f"Gaze: {result['gaze_score']:.2f} | "
              f"Emotion: {result['dominant_emotion']:8s} | "
              f"Direction: {result['gaze_direction']:6s}")
    
    def _draw_analysis_overlay(self, frame, result):
        """Draw analysis overlay on frame"""
        annotated_frame = frame.copy()
        
        if result:
            # Draw engagement score
            engagement_text = f"Engagement: {result['engagement_score']:.2f}"
            cv2.putText(annotated_frame, engagement_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Draw face detection status
            face_text = f"Face: {'Detected' if result['face_detected'] else 'Not Detected'}"
            color = (0, 255, 0) if result['face_detected'] else (0, 0, 255)
            cv2.putText(annotated_frame, face_text, (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # Draw emotion
            emotion_text = f"Emotion: {result['dominant_emotion']}"
            cv2.putText(annotated_frame, emotion_text, (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Draw gaze direction
            gaze_text = f"Gaze: {result['gaze_direction']}"
            cv2.putText(annotated_frame, gaze_text, (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
        
        # Draw demo info
        cv2.putText(annotated_frame, "DEMO MODE - Press 'q' to quit", 
                   (10, annotated_frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return annotated_frame
    
    def _print_summary(self, history):
        """Print demo summary"""
        if not history:
            print("No data collected during demo")
            return
        
        # Calculate statistics
        engagement_scores = [r['engagement_score'] for r in history if r['face_detected']]
        
        if engagement_scores:
            avg_engagement = np.mean(engagement_scores)
            max_engagement = np.max(engagement_scores)
            min_engagement = np.min(engagement_scores)
            
            print("\n" + "="*50)
            print("DEMO SUMMARY")
            print("="*50)
            print(f"Total frames analyzed: {len(history)}")
            print(f"Frames with face detected: {len(engagement_scores)}")
            print(f"Detection rate: {len(engagement_scores)/len(history)*100:.1f}%")
            print(f"Average engagement: {avg_engagement:.3f}")
            print(f"Max engagement: {max_engagement:.3f}")
            print(f"Min engagement: {min_engagement:.3f}")
            
            # Emotion distribution
            emotions = [r['dominant_emotion'] for r in history if r['face_detected']]
            emotion_counts = {}
            for emotion in emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            print("\nEmotion distribution:")
            for emotion, count in sorted(emotion_counts.items()):
                percentage = count / len(emotions) * 100
                print(f"  {emotion}: {count} ({percentage:.1f}%)")
            
            print(f"\nData stored in database with session ID: {self.session_id}")
        else:
            print("No valid engagement data collected (no faces detected)")

def main():
    """Main demo function"""
    parser = argparse.ArgumentParser(description='Student Engagement Analysis Demo')
    parser.add_argument('--video', type=str, help='Path to video file (default: use webcam)')
    parser.add_argument('--duration', type=int, default=60, help='Demo duration in seconds (default: 60)')
    
    args = parser.parse_args()
    
    # Create demo instance
    demo = EngagementDemo(
        use_webcam=(args.video is None),
        video_path=args.video
    )
    
    # Run demo
    demo.run_analysis(args.duration)

if __name__ == "__main__":
    main()