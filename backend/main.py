"""
Main FastAPI application for Student Engagement Analysis Tool
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import cv2
import numpy as np
import base64
from typing import List, Dict, Any
import asyncio
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.engagement_analyzer import EngagementAnalyzer
from models.gemini_analyzer import gemini_analyzer
from database.connection import get_db_session
from database.models import EngagementRecord
from backend.config import settings

app = FastAPI(title="Student Engagement API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engagement analyzer
analyzer = EngagementAnalyzer()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "Student Engagement Analysis API"}

@app.post("/analyze-frame")
async def analyze_frame(file: UploadFile = File(...)):
    """Analyze a single frame for engagement metrics"""
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Analyze engagement
        result = analyzer.analyze_frame(frame)
        
        # Store in database
        db = next(get_db_session())
        record = EngagementRecord(
            student_id=result.get('student_id', 'unknown'),
            session_id=result.get('session_id', 'default'),
            engagement_score=result['engagement_score'],
            face_detected=result['face_detected'],
            gaze_score=result['gaze_score'],
            emotion_score=result['emotion_score'],
            presence_score=result['presence_score']
        )
        db.add(record)
        db.commit()
        
        return JSONResponse(content=result)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.websocket("/ws/engagement")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time engagement analysis"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive frame data
            data = await websocket.receive_text()
            frame_data = json.loads(data)
            
            # Decode base64 image
            image_data = base64.b64decode(frame_data['image'])
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Analyze engagement
            result = analyzer.analyze_frame(frame)
            
            # Send result back
            await websocket.send_text(json.dumps(result))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/engagement/history/{student_id}")
async def get_engagement_history(student_id: str, limit: int = 100):
    """Get engagement history for a student"""
    db = next(get_db_session())
    records = db.query(EngagementRecord).filter(
        EngagementRecord.student_id == student_id
    ).order_by(EngagementRecord.timestamp.desc()).limit(limit).all()
    
    # Generate AI feedback
    record_data = [{
        "engagement_score": r.engagement_score,
        "face_detected": r.face_detected,
        "dominant_emotion": r.dominant_emotion,
        "session_id": r.session_id
    } for r in records]
    
    ai_feedback = gemini_analyzer.generate_student_feedback(record_data)
    
    return {
        "student_id": student_id,
        "ai_feedback": ai_feedback,
        "records": [
            {
                "timestamp": record.timestamp.isoformat(),
                "engagement_score": record.engagement_score,
                "face_detected": record.face_detected,
                "gaze_score": record.gaze_score,
                "emotion_score": record.emotion_score,
                "presence_score": record.presence_score
            }
            for record in records
        ]
    }

@app.get("/engagement/session/{session_id}")
async def get_session_engagement(session_id: str):
    """Get engagement data for a session"""
    db = next(get_db_session())
    records = db.query(EngagementRecord).filter(
        EngagementRecord.session_id == session_id
    ).all()
    
    # Calculate session statistics
    if not records:
        return {"message": "No data found for session"}
    
    avg_engagement = sum(r.engagement_score for r in records) / len(records)
    total_students = len(set(r.student_id for r in records))
    
    # Generate AI summary
    record_data = [{
        "student_id": r.student_id,
        "engagement_score": r.engagement_score,
        "face_detected": r.face_detected,
        "dominant_emotion": r.dominant_emotion
    } for r in records]
    
    ai_summary = gemini_analyzer.generate_session_summary(record_data)
    
    return {
        "session_id": session_id,
        "average_engagement": avg_engagement,
        "total_students": total_students,
        "total_records": len(records),
        "ai_summary": ai_summary,
        "records": [
            {
                "student_id": r.student_id,
                "timestamp": r.timestamp.isoformat(),
                "engagement_score": r.engagement_score
            }
            for r in records
        ]
    }

@app.get("/engagement/session/{session_id}/detailed")
async def get_session_detailed(session_id: str):
    """Get detailed per-student breakdown for a session"""
    db = next(get_db_session())
    records = db.query(EngagementRecord).filter(
        EngagementRecord.session_id == session_id
    ).order_by(EngagementRecord.timestamp).all()

    if not records:
        return {"message": "No data found for session"}

    # Per-student stats
    students = {}
    for r in records:
        sid = r.student_id
        if sid not in students:
            students[sid] = {"scores": [], "emotions": [], "gaze": [], "timestamps": []}
        students[sid]["scores"].append(r.engagement_score)
        students[sid]["gaze"].append(r.gaze_score or 0)
        students[sid]["timestamps"].append(r.timestamp.isoformat())
        if r.dominant_emotion:
            students[sid]["emotions"].append(r.dominant_emotion)

    student_stats = []
    for sid, data in students.items():
        scores = data["scores"]
        emotion_counts = {}
        for e in data["emotions"]:
            emotion_counts[e] = emotion_counts.get(e, 0) + 1
        top_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else "neutral"
        student_stats.append({
            "student_id": sid,
            "avg_engagement": round(sum(scores) / len(scores), 3),
            "max_engagement": round(max(scores), 3),
            "min_engagement": round(min(scores), 3),
            "avg_gaze": round(sum(data["gaze"]) / len(data["gaze"]), 3),
            "data_points": len(scores),
            "dominant_emotion": top_emotion,
            "emotion_distribution": emotion_counts,
            "timeline": [{"t": t, "score": s} for t, s in zip(data["timestamps"], scores)]
        })

    # Engagement over time (all students averaged per minute)
    from collections import defaultdict
    time_buckets = defaultdict(list)
    for r in records:
        minute = r.timestamp.strftime("%H:%M")
        time_buckets[minute].append(r.engagement_score)
    timeline = [{"time": t, "avg": round(sum(v)/len(v), 3)} for t, v in sorted(time_buckets.items())]

    # Overall emotion distribution
    all_emotions = {}
    for r in records:
        if r.dominant_emotion:
            all_emotions[r.dominant_emotion] = all_emotions.get(r.dominant_emotion, 0) + 1

    all_scores = [r.engagement_score for r in records]
    return {
        "session_id": session_id,
        "total_students": len(students),
        "total_records": len(records),
        "avg_engagement": round(sum(all_scores) / len(all_scores), 3),
        "high_engagement_pct": round(len([s for s in all_scores if s >= 0.7]) / len(all_scores) * 100, 1),
        "low_engagement_pct": round(len([s for s in all_scores if s < 0.4]) / len(all_scores) * 100, 1),
        "emotion_distribution": all_emotions,
        "engagement_timeline": timeline,
        "students": student_stats
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )