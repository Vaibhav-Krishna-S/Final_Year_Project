# Student Engagement Analysis Tool

An advanced AI-powered tool that analyzes student attentiveness during online/hybrid classes using computer vision and machine learning.

## Features

- Real-time face detection and gaze tracking
- Emotion recognition and engagement scoring
- LMS integration (Moodle, Canvas, Google Classroom)
- Interactive dashboard with visual analytics
- Privacy-compliant (no raw video storage)

## Architecture

```
student-engagement-ai/
├── frontend/          # React UI for webcam capture
├── backend/           # FastAPI server for ML inference
├── models/            # AI/ML models (face, gaze, emotion)
├── dashboard/         # Visualization dashboard
├── database/          # Data storage layer
├── integration/       # LMS API connectors
└── tests/            # Unit tests
```

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start backend server:
```bash
cd backend && python main.py
```

3. Start frontend:
```bash
cd frontend && npm start
```

4. Access dashboard at `http://localhost:3000`

## AI Models Used

- **Face Detection**: Mediapipe Face Detection
- **Gaze Estimation**: Mediapipe Face Mesh
- **Emotion Recognition**: DeepFace
- **Engagement Scoring**: Custom weighted algorithm

## Privacy & Compliance

- No raw video data stored
- Only derived analytics retained
- GDPR/FERPA compliant design
- Configurable data retention policies