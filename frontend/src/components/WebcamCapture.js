import React, { useRef, useCallback, useState, useEffect } from 'react';
import Webcam from 'react-webcam';
import { 
  Box, 
  Button, 
  Typography, 
  Card, 
  CardContent,
  Alert,
  CircularProgress
} from '@mui/material';
import { VideocamOff, Videocam } from '@mui/icons-material';
import io from 'socket.io-client';

const WebcamCapture = ({ onEngagementUpdate, studentId = 'student_1' }) => {
  const webcamRef = useRef(null);
  const [isCapturing, setIsCapturing] = useState(false);
  const [socket, setSocket] = useState(null);
  const [currentEngagement, setCurrentEngagement] = useState(null);
  const [error, setError] = useState(null);

  // WebSocket connection
  useEffect(() => {
    const newSocket = io('ws://localhost:8000');
    setSocket(newSocket);

    newSocket.on('connect', () => {
      console.log('Connected to engagement analysis server');
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server');
    });

    return () => newSocket.close();
  }, []);

  // Capture and analyze frames
  const captureFrame = useCallback(() => {
    if (!webcamRef.current || !socket) return;

    const imageSrc = webcamRef.current.getScreenshot();
    if (imageSrc) {
      // Remove data URL prefix
      const base64Data = imageSrc.split(',')[1];
      
      // Send frame to backend for analysis
      socket.emit('analyze_frame', {
        image: base64Data,
        student_id: studentId,
        timestamp: new Date().toISOString()
      });

      // Listen for analysis results
      socket.on('engagement_result', (result) => {
        setCurrentEngagement(result);
        if (onEngagementUpdate) {
          onEngagementUpdate(result);
        }
      });
    }
  }, [socket, studentId, onEngagementUpdate]);

  // Start/stop capturing
  const toggleCapture = () => {
    if (isCapturing) {
      setIsCapturing(false);
      setCurrentEngagement(null);
    } else {
      setIsCapturing(true);
      setError(null);
    }
  };

  // Capture frames at regular intervals
  useEffect(() => {
    let interval;
    if (isCapturing) {
      interval = setInterval(captureFrame, 2000); // Capture every 2 seconds
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isCapturing, captureFrame]);

  const videoConstraints = {
    width: 640,
    height: 480,
    facingMode: "user"
  };

  const getEngagementColor = (score) => {
    if (score >= 0.7) return '#4caf50'; // Green
    if (score >= 0.4) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
      <Card sx={{ maxWidth: 700 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Webcam Feed
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ position: 'relative', display: 'inline-block' }}>
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={videoConstraints}
              onUserMediaError={(error) => {
                setError('Camera access denied. Please allow camera permissions.');
                console.error('Webcam error:', error);
              }}
              style={{
                width: '100%',
                maxWidth: 640,
                height: 'auto',
                borderRadius: 8
              }}
            />
            
            {isCapturing && (
              <Box
                sx={{
                  position: 'absolute',
                  top: 10,
                  right: 10,
                  backgroundColor: 'rgba(0,0,0,0.7)',
                  color: 'white',
                  padding: 1,
                  borderRadius: 1,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1
                }}
              >
                <CircularProgress size={16} color="inherit" />
                <Typography variant="caption">Analyzing...</Typography>
              </Box>
            )}
          </Box>

          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
            <Button
              variant="contained"
              onClick={toggleCapture}
              startIcon={isCapturing ? <VideocamOff /> : <Videocam />}
              color={isCapturing ? "secondary" : "primary"}
            >
              {isCapturing ? 'Stop Analysis' : 'Start Analysis'}
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Engagement Display */}
      {currentEngagement && (
        <Card sx={{ minWidth: 300 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Real-time Engagement
            </Typography>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Overall Score:</Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: getEngagementColor(currentEngagement.engagement_score),
                    fontWeight: 'bold'
                  }}
                >
                  {(currentEngagement.engagement_score * 100).toFixed(1)}%
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Attention:</Typography>
                <Typography variant="body2">
                  {(currentEngagement.gaze_score * 100).toFixed(1)}%
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Emotion:</Typography>
                <Typography variant="body2">
                  {currentEngagement.dominant_emotion}
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Presence:</Typography>
                <Typography variant="body2">
                  {currentEngagement.face_detected ? 'Detected' : 'Not Detected'}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default WebcamCapture;