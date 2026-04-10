# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API does not require authentication for demo purposes. In production, implement proper authentication mechanisms.

## Endpoints

### Health Check

#### GET /
Check if the API is running.

**Response:**
```json
{
  "message": "Student Engagement Analysis API"
}
```

### Frame Analysis

#### POST /analyze-frame
Analyze a single frame for engagement metrics.

**Request:**
- Content-Type: `multipart/form-data`
- Body: Image file

**Response:**
```json
{
  "student_id": "student_123",
  "session_id": "session_456",
  "face_detected": true,
  "gaze_score": 0.85,
  "emotion_score": 0.72,
  "presence_score": 1.0,
  "posture_score": 0.68,
  "engagement_score": 0.78,
  "dominant_emotion": "happy",
  "gaze_direction": "center"
}
```

### WebSocket Endpoints

#### WS /ws/engagement
Real-time engagement analysis via WebSocket.

**Send:**
```json
{
  "image": "base64_encoded_image_data",
  "student_id": "student_123",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Receive:**
```json
{
  "student_id": "student_123",
  "engagement_score": 0.78,
  "face_detected": true,
  "gaze_score": 0.85,
  "emotion_score": 0.72,
  "dominant_emotion": "happy",
  "gaze_direction": "center",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Engagement History

#### GET /engagement/history/{student_id}
Get engagement history for a specific student.

**Parameters:**
- `student_id` (path): Student identifier
- `limit` (query, optional): Number of records to return (default: 100)

**Response:**
```json
[
  {
    "timestamp": "2024-01-01T12:00:00Z",
    "engagement_score": 0.78,
    "face_detected": true,
    "gaze_score": 0.85,
    "emotion_score": 0.72,
    "presence_score": 1.0
  }
]
```

#### GET /engagement/session/{session_id}
Get engagement data for a session.

**Parameters:**
- `session_id` (path): Session identifier

**Response:**
```json
{
  "session_id": "session_456",
  "average_engagement": 0.75,
  "total_students": 25,
  "total_records": 1500,
  "records": [
    {
      "student_id": "student_123",
      "timestamp": "2024-01-01T12:00:00Z",
      "engagement_score": 0.78
    }
  ]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request format"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error message"
}
```

## Rate Limiting

Currently no rate limiting is implemented. In production, consider implementing:
- Per-IP rate limiting
- Per-user rate limiting
- WebSocket connection limits

## Data Models

### Engagement Result
```json
{
  "student_id": "string",
  "session_id": "string", 
  "timestamp": "ISO 8601 datetime",
  "engagement_score": "float (0-1)",
  "face_detected": "boolean",
  "gaze_score": "float (0-1)",
  "emotion_score": "float (0-1)",
  "presence_score": "float (0-1)",
  "posture_score": "float (0-1)",
  "dominant_emotion": "string",
  "gaze_direction": "string (left|center|right)",
  "confidence_level": "float (0-1)"
}
```

### Session Summary
```json
{
  "session_id": "string",
  "course_id": "string",
  "start_time": "ISO 8601 datetime",
  "end_time": "ISO 8601 datetime",
  "average_engagement": "float (0-1)",
  "total_students": "integer",
  "total_records": "integer",
  "attention_rate": "float (0-1)"
}
```

## SDK Examples

### Python
```python
import requests
import base64

# Analyze frame
with open('frame.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/analyze-frame', files=files)
    result = response.json()
    print(f"Engagement Score: {result['engagement_score']}")

# Get student history
response = requests.get('http://localhost:8000/engagement/history/student_123')
history = response.json()
```

### JavaScript
```javascript
// Analyze frame
const formData = new FormData();
formData.append('file', imageFile);

fetch('http://localhost:8000/analyze-frame', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Engagement Score:', data.engagement_score);
});

// WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws/engagement');

ws.onopen = function() {
  // Send frame data
  ws.send(JSON.stringify({
    image: base64ImageData,
    student_id: 'student_123',
    timestamp: new Date().toISOString()
  }));
};

ws.onmessage = function(event) {
  const result = JSON.parse(event.data);
  console.log('Real-time engagement:', result.engagement_score);
};
```

## Webhook Integration

For LMS integration, the system can send webhook notifications:

### Engagement Alert Webhook
```json
{
  "event": "engagement_alert",
  "student_id": "student_123",
  "session_id": "session_456",
  "alert_type": "low_engagement",
  "engagement_score": 0.25,
  "threshold": 0.5,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Session Summary Webhook
```json
{
  "event": "session_completed",
  "session_id": "session_456",
  "summary": {
    "average_engagement": 0.75,
    "total_students": 25,
    "duration_minutes": 90
  },
  "timestamp": "2024-01-01T13:30:00Z"
}
```