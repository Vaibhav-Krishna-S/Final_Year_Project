# Student Engagement AI — Complete Project Explanation

---

## 1. Problem Statement

Online and hybrid learning has exploded in adoption, but it comes with a fundamental blind spot: instructors cannot tell if students are actually paying attention. In a physical classroom, a teacher can scan the room and immediately sense who is engaged, confused, or zoned out. That feedback loop disappears on a screen.

The consequences are real:
- Students disengage silently without anyone noticing
- Instructors have no data to adjust their teaching in real time
- Institutions lack objective metrics to evaluate teaching effectiveness
- Students themselves often don't realize how distracted they are

This project solves that problem by using a student's own webcam to automatically measure engagement — no manual input, no surveys, no guesswork. It analyzes facial cues, eye movement, and emotional state to produce a continuous engagement score, and surfaces that data to both students and instructors through live dashboards.

---

## 2. What the System Does

At a high level, the system:

1. Captures webcam frames from a student's browser every ~2 seconds
2. Runs those frames through a pipeline of AI/ML models (face detection → gaze tracking → emotion recognition)
3. Combines the outputs into a single engagement score (0 to 1)
4. Stores the score in a database
5. Displays real-time feedback to the student and aggregated analytics to the instructor
6. Optionally syncs engagement scores as grades back to an LMS (Canvas, Moodle)
7. Uses Google Gemini to generate natural-language summaries and personalized feedback

Critically, no raw video is ever stored — only the derived metrics. This makes the system privacy-compliant by design.

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                      │
│   StudentView  ←→  WebcamCapture  ←→  InstructorDashboard   │
└────────────────────────┬────────────────────────────────────┘
                         │  WebSocket (Socket.IO) + REST
┌────────────────────────▼────────────────────────────────────┐
│                     BACKEND (FastAPI)                        │
│         WebSocket handler + REST endpoints + CORS            │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    AI/ML MODELS (Python)                     │
│   FaceDetector → GazeEstimator → EmotionDetector            │
│                       ↓                                      │
│              EngagementAnalyzer (weighted score)             │
│                       ↓                                      │
│              GeminiAnalyzer (AI feedback)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  DATABASE (SQLAlchemy ORM)                   │
│         SQLite (dev)  /  PostgreSQL (production)             │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│               LMS INTEGRATION (Optional)                     │
│              Canvas  /  Moodle  /  Mock LMS                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | React 18 + Material-UI | Modern, component-based UI with professional design system |
| Charts | Chart.js + react-chartjs-2 | Interactive line, bar, and doughnut charts |
| Real-time comms | Socket.IO | Bidirectional WebSocket for live frame streaming |
| Webcam | react-webcam | Simple browser webcam access |
| Backend | FastAPI + Uvicorn | Async Python web framework, fast and type-safe |
| Computer Vision | OpenCV | Frame decoding and image processing |
| Face/Gaze | MediaPipe | Google's ML framework for face mesh and landmark detection |
| Emotion | DeepFace (+ heuristic fallback) | Facial emotion recognition |
| AI Insights | Google Gemini 1.5 Pro | Natural language session summaries and feedback |
| ORM | SQLAlchemy | Database abstraction supporting SQLite and PostgreSQL |
| Dashboard | Plotly Dash | Python-native interactive analytics dashboard |
| Config | python-dotenv | Environment-based secrets and settings management |

---

## 5. Project Structure

```
student-engagement-ai/
├── backend/
│   ├── main.py          # FastAPI app, WebSocket handler, REST endpoints
│   └── config.py        # All settings loaded from .env
├── models/
│   ├── face_detector.py      # MediaPipe face detection
│   ├── gaze_estimator.py     # Eye tracking via Face Mesh
│   ├── emotion_detector.py   # Emotion recognition
│   ├── engagement_analyzer.py # Orchestrates all models, computes score
│   └── gemini_analyzer.py    # Gemini AI for insights and feedback
├── database/
│   ├── models.py        # SQLAlchemy ORM models
│   └── connection.py    # Engine, session factory, CRUD helpers
├── frontend/
│   └── src/
│       ├── App.js                        # Router + theme
│       ├── pages/StudentView.js          # Student session UI
│       ├── pages/InstructorDashboard.js  # Analytics dashboard
│       └── components/WebcamCapture.js   # Webcam + Socket.IO
├── integration/
│   ├── lms_connector.py  # Canvas + Moodle connectors
│   └── mock_lms.py       # Mock LMS for testing
├── dashboard/
│   └── app.py            # Plotly Dash analytics app
├── tests/
│   └── test_engagement_analyzer.py
├── .env                  # Secrets and config (not committed)
├── requirements.txt      # Python dependencies
└── setup.py              # Automated setup script
```

---

## 6. AI/ML Pipeline — How It Works

Every 2 seconds, a webcam frame travels through this pipeline:

### Step 1 — Face Detection (`face_detector.py`)
- Uses MediaPipe Face Detection
- Detects faces and returns bounding boxes + keypoints
- Confidence threshold: 0.7 (configurable)
- If no face is detected, presence_score = 0 and the pipeline short-circuits

### Step 2 — Gaze Estimation (`gaze_estimator.py`)
- Uses MediaPipe Face Mesh (468 facial landmarks)
- Extracts iris positions relative to eye corners
- Calculates a ratio: where is the iris within the eye socket?
- Applies a Gaussian function — score peaks at 0.5 (center gaze) and drops off toward edges
- Outputs: attention_score (0–1) and direction (left / center / right)

### Step 3 — Emotion Recognition (`emotion_detector.py`)
- Analyzes the cropped face region
- Maps detected emotion to an engagement value:

| Emotion | Engagement Score |
|---|---|
| Happy | 0.9 |
| Focused | 0.85 |
| Surprised | 0.8 |
| Neutral | 0.6 |
| Fear | 0.4 |
| Sad | 0.3 |
| Disgust | 0.2 |
| Angry | 0.1 |

### Step 4 — Engagement Score (`engagement_analyzer.py`)
Combines all signals using a weighted formula:

```
Engagement = (0.30 × gaze_score)
           + (0.25 × emotion_score)
           + (0.25 × presence_score)
           + (0.20 × posture_score)
```

All weights are configurable via `.env`. The result is a float between 0 and 1:

| Score Range | Label | Color |
|---|---|---|
| 0.7 – 1.0 | High | Green |
| 0.4 – 0.7 | Moderate | Orange |
| 0.0 – 0.4 | Low | Red |

### Step 5 — AI Feedback (`gemini_analyzer.py`)
- Sends aggregated session stats to Google Gemini 1.5 Pro
- Generates a 2–3 sentence natural language summary
- Produces personalized feedback per student
- Falls back to heuristic summaries if the API key is not configured

---

## 7. Data Flow — End to End

```
1. Student opens browser → enters Student ID + Session ID → clicks Start

2. WebcamCapture.js starts capturing frames every 2 seconds
   → Converts frame to base64 JPEG
   → Emits via Socket.IO: { image, student_id, timestamp }

3. FastAPI WebSocket handler receives frame
   → Decodes base64 → OpenCV numpy array
   → Calls EngagementAnalyzer.analyze_frame()

4. EngagementAnalyzer runs the pipeline:
   FaceDetector → GazeEstimator → EmotionDetector → weighted score

5. Result stored in database as EngagementRecord:
   { student_id, session_id, timestamp, engagement_score,
     gaze_score, emotion_score, presence_score, posture_score,
     dominant_emotion, gaze_direction }

6. Result emitted back via WebSocket → displayed in StudentView

7. Instructor opens /dashboard → enters Session ID → clicks Load
   → GET /engagement/session/{id}/detailed
   → Backend aggregates all records for that session
   → Returns per-student stats + timeline data

8. (Optional) LMS sync:
   → Engagement scores converted to 0–100 grade scale
   → Submitted to Canvas/Moodle via REST API
```

---

## 8. Database Models

### `students`
Stores student identity. Fields: `id`, `name`, `email`, `lms_id`, `created_at`

### `sessions`
Represents a class session. Fields: `id`, `course_id`, `course_name`, `instructor_id`, `start_time`, `end_time`, `status`

### `engagement_records`
One row per frame analysis. Fields: `student_id`, `session_id`, `timestamp`, `engagement_score`, `gaze_score`, `emotion_score`, `presence_score`, `posture_score`, `dominant_emotion`, `gaze_direction`

### `engagement_summaries`
Aggregated per student per session. Fields: `avg_engagement`, `max/min/std`, `attention_rate`, `emotion_distribution`

### `alerts`
Triggered when engagement drops below threshold. Fields: `student_id`, `alert_type`, `severity`, `threshold_value`, `status`

### `lms_integrations`
LMS configuration and sync state. Fields: `lms_type`, `lms_instance_url`, `sync_status`, `last_sync_at`

---

## 9. Frontend — Two Views

### Student View (`/student`)
- Enter Student ID and Session ID to start a session
- Live webcam feed with engagement overlay
- Real-time display of: engagement score, dominant emotion, gaze direction
- Running average engagement for the session
- Privacy notice (no video stored)

### Instructor Dashboard (`/dashboard`)
- Enter Session ID to load analytics
- Summary stat cards: average engagement, total students, attention rate
- Line chart: engagement timeline over the session
- Bar chart: per-student engagement comparison
- Doughnut chart: emotion distribution across the class
- Per-student table with individual breakdowns
- Auto-refresh toggle (every 10 seconds for live sessions)
- AI-generated session summary from Gemini

---

## 10. Backend API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/analyze-frame` | Single frame analysis (REST) |
| WebSocket | `/ws/engagement` | Real-time frame streaming |
| GET | `/engagement/history/{student_id}` | Student's engagement history + AI feedback |
| GET | `/engagement/session/{session_id}` | Session-level aggregated stats |
| GET | `/engagement/session/{session_id}/detailed` | Per-student breakdown with timelines |

---

## 11. LMS Integration

The integration layer uses an abstract `LMSConnector` base class with concrete implementations for:

- `CanvasConnector` — Canvas REST API with Bearer token auth
- `MoodleConnector` — Moodle web services API
- `MockLMSConnector` — In-memory mock for development/testing

The `LMSIntegrationManager` acts as a factory, selecting the right connector based on the `LMS_TYPE` environment variable.

Workflow:
1. Retrieve enrolled students from LMS
2. Create an "Engagement Score" assignment
3. Convert engagement scores (0–1) → grades (0–100)
4. Submit grades via LMS API

---

## 12. Configuration (`.env`)

```env
DATABASE_URL=sqlite:///./engagement.db
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-pro

LMS_TYPE=mock                    # mock | canvas | moodle
LMS_BASE_URL=https://your-lms.edu
LMS_API_KEY=your_lms_api_key
LMS_CLIENT_ID=your_client_id
LMS_CLIENT_SECRET=your_client_secret

SECRET_KEY=your-secret-key

# Engagement scoring weights (must sum to 1.0)
WEIGHT_EYE_CONTACT=0.3
WEIGHT_EMOTION=0.25
WEIGHT_PRESENCE=0.25
WEIGHT_POSTURE=0.2

# Detection confidence thresholds
FACE_DETECTION_CONFIDENCE=0.7
EMOTION_DETECTION_CONFIDENCE=0.6
ENGAGEMENT_THRESHOLD=0.5
```

---

## 13. Privacy & Compliance

The system is designed privacy-first:

- No raw video frames are ever stored — only derived numeric metrics
- Students are identified by ID, not biometric data
- GDPR/FERPA compliant architecture
- Configurable data retention policies
- All secrets externalized via environment variables

For production, the following additions are recommended:
- JWT authentication on all API endpoints
- HTTPS/WSS for encrypted transport
- Rate limiting on the analysis endpoints
- Role-based access control (students vs instructors vs admins)
- Audit logging for data access

---

## 14. How to Run

### Backend
```bash
cd student-engagement-ai
pip install -r requirements.txt
python backend/main.py
# Runs on http://localhost:8000
```

### Frontend
```bash
cd student-engagement-ai/frontend
npm install
npm start
# Runs on http://localhost:3000
```

### Plotly Dash Dashboard (alternative analytics view)
```bash
cd student-engagement-ai
python dashboard/app.py
```

### Demo (no frontend needed)
```bash
cd student-engagement-ai
python run_demo.py
```

### Add Sample Data
```bash
cd student-engagement-ai
python add_sample_data.py
```

---

## 15. Key Design Decisions

**Weighted scoring over a single model** — No single signal is reliable enough on its own. Combining gaze, emotion, presence, and posture with configurable weights produces a more robust and tunable metric.

**WebSocket over polling** — Real-time feedback requires low latency. WebSocket eliminates the overhead of repeated HTTP requests and enables true push-based updates.

**Privacy by design** — Storing only metrics (not frames) was a deliberate architectural choice, not an afterthought. This makes GDPR/FERPA compliance structural rather than procedural.

**Abstract LMS connector** — The `LMSConnector` base class means adding support for a new LMS (e.g., Blackboard) requires only implementing a new subclass, not touching any existing code.

**Gemini as an optional layer** — The system works fully without a Gemini API key. The `GeminiAnalyzer` falls back to heuristic summaries, so the core functionality is never blocked by an external dependency.

**SQLite for dev, PostgreSQL for prod** — The SQLAlchemy abstraction means the same codebase runs locally with zero setup and scales to a production database with a single config change.

---

## 16. Future Enhancements

- Voice tone analysis for multimodal engagement signals
- Full body pose estimation for richer posture scoring
- Predictive alerts: ML model to flag students likely to disengage
- Mobile app for student self-monitoring
- Multi-camera support for physical classrooms
- Real-time instructor nudges powered by Gemini
- Support for additional LMS platforms (Blackboard, Google Classroom)
- Alembic database migrations for schema evolution
