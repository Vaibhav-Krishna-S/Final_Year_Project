# Installation Guide

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher (for frontend)
- PostgreSQL (optional, SQLite used by default)
- Webcam or video files for testing

## Quick Setup

1. **Clone and navigate to project:**
```bash
cd student-engagement-ai
```

2. **Run automated setup:**
```bash
python setup.py
```

3. **Update configuration:**
   - Copy `.env.example` to `.env`
   - Update database and API settings

## Manual Installation

### Backend Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Initialize database:**
```bash
python -c "from database.connection import create_tables; create_tables()"
```

3. **Start backend server:**
```bash
cd backend
python main.py
```

### Frontend Setup

1. **Install Node.js dependencies:**
```bash
cd frontend
npm install
```

2. **Start development server:**
```bash
npm start
```

### Dashboard Setup

1. **Start dashboard:**
```bash
python dashboard/app.py
```

## Configuration

### Environment Variables

Create `.env` file with:

```env
# Database
DATABASE_URL=sqlite:///./engagement.db

# API Keys (optional)
OPENAI_API_KEY=your_key_here
LMS_API_KEY=your_lms_key

# LMS Integration
LMS_TYPE=canvas
LMS_BASE_URL=https://your-lms.com
LMS_CLIENT_ID=your_client_id
LMS_CLIENT_SECRET=your_client_secret

# Model Settings
FACE_DETECTION_CONFIDENCE=0.7
EMOTION_DETECTION_CONFIDENCE=0.6
ENGAGEMENT_THRESHOLD=0.5
```

### Database Configuration

**SQLite (Default):**
```env
DATABASE_URL=sqlite:///./engagement.db
```

**PostgreSQL:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/engagement_db
```

## Testing

### Run Unit Tests
```bash
pytest tests/
```

### Run Demo
```bash
# With webcam
python run_demo.py

# With video file
python run_demo.py --video path/to/video.mp4

# Custom duration
python run_demo.py --duration 120
```

## Troubleshooting

### Common Issues

1. **Camera Access Denied:**
   - Check browser permissions
   - Ensure no other applications are using the camera

2. **Module Import Errors:**
   - Verify Python path includes project directory
   - Check all dependencies are installed

3. **Database Connection Issues:**
   - Verify database URL in `.env`
   - Check database server is running (for PostgreSQL)

4. **Model Loading Errors:**
   - Ensure sufficient disk space for model downloads
   - Check internet connection for first-time model downloads

### Performance Optimization

1. **Reduce Analysis Frequency:**
   - Modify capture interval in WebcamCapture component
   - Adjust frame processing rate in backend

2. **Model Optimization:**
   - Use smaller model variants for faster inference
   - Implement frame skipping for real-time performance

3. **Database Optimization:**
   - Use PostgreSQL for production
   - Implement data archiving for old records

## Production Deployment

### Backend Deployment

1. **Use production WSGI server:**
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
```

2. **Configure reverse proxy (nginx):**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Frontend Deployment

1. **Build production bundle:**
```bash
cd frontend
npm run build
```

2. **Serve static files:**
   - Use nginx, Apache, or CDN
   - Configure API proxy to backend

### Security Considerations

- Use HTTPS in production
- Implement proper authentication
- Secure API endpoints
- Regular security updates
- Data encryption at rest

## Support

For issues and questions:
- Check troubleshooting section
- Review logs in `logs/` directory
- Create GitHub issue with error details