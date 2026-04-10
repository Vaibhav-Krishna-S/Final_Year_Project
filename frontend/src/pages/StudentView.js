import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Alert
} from '@mui/material';
import { School, Person } from '@mui/icons-material';
import WebcamCapture from '../components/WebcamCapture';

const StudentView = () => {
  const [studentId, setStudentId] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [engagementHistory, setEngagementHistory] = useState([]);

  const handleStartSession = () => {
    if (studentId.trim() && sessionId.trim()) {
      setIsSessionActive(true);
    }
  };

  const handleEndSession = () => {
    setIsSessionActive(false);
    setEngagementHistory([]);
  };

  const handleEngagementUpdate = (engagementData) => {
    setEngagementHistory(prev => [...prev.slice(-50), engagementData]); // Keep last 50 records
  };

  const getAverageEngagement = () => {
    if (engagementHistory.length === 0) return 0;
    const sum = engagementHistory.reduce((acc, curr) => acc + curr.engagement_score, 0);
    return (sum / engagementHistory.length * 100).toFixed(1);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <School color="primary" />
        Student Engagement Monitor
      </Typography>

      {!isSessionActive ? (
        <Card sx={{ maxWidth: 500, mx: 'auto', mt: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Person />
              Join Session
            </Typography>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
              <TextField
                label="Student ID"
                value={studentId}
                onChange={(e) => setStudentId(e.target.value)}
                placeholder="Enter your student ID"
                fullWidth
              />
              
              <TextField
                label="Session ID"
                value={sessionId}
                onChange={(e) => setSessionId(e.target.value)}
                placeholder="Enter session/class ID"
                fullWidth
              />
              
              <Button
                variant="contained"
                onClick={handleStartSession}
                disabled={!studentId.trim() || !sessionId.trim()}
                size="large"
              >
                Start Engagement Monitoring
              </Button>
            </Box>

            <Alert severity="info" sx={{ mt: 2 }}>
              Your engagement will be monitored during the session. No video data is stored - only engagement metrics.
            </Alert>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <WebcamCapture
              onEngagementUpdate={handleEngagementUpdate}
              studentId={studentId}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Session Info
                </Typography>
                
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mb: 2 }}>
                  <Typography variant="body2">
                    <strong>Student:</strong> {studentId}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Session:</strong> {sessionId}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Status:</strong> Active
                  </Typography>
                </Box>

                <Button
                  variant="outlined"
                  color="secondary"
                  onClick={handleEndSession}
                  fullWidth
                >
                  End Session
                </Button>
              </CardContent>
            </Card>

            {engagementHistory.length > 0 && (
              <Card sx={{ mt: 2 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Session Statistics
                  </Typography>
                  
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Typography variant="body2">
                      <strong>Average Engagement:</strong> {getAverageEngagement()}%
                    </Typography>
                    <Typography variant="body2">
                      <strong>Data Points:</strong> {engagementHistory.length}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Duration:</strong> {Math.floor(engagementHistory.length * 2 / 60)} min
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            )}

            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Privacy Notice
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • No video recordings are stored
                  • Only engagement metrics are collected
                  • Data is used for educational improvement
                  • You can stop monitoring at any time
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default StudentView;