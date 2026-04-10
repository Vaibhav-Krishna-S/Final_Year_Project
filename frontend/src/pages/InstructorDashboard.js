import React, { useState, useEffect, useCallback } from 'react';
import {
    Box, Typography, Card, CardContent, Grid, TextField, Button,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    Paper, Chip, Alert, LinearProgress, Avatar, Divider, IconButton, Tooltip
} from '@mui/material';
import {
    Dashboard, Search, Refresh, TrendingUp, TrendingDown, People,
    EmojiEmotions, Visibility, Psychology
} from '@mui/icons-material';
import {
    Chart as ChartJS, CategoryScale, LinearScale, PointElement,
    LineElement, BarElement, ArcElement, Title, Tooltip as ChartTooltip, Legend, Filler
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale, LinearScale, PointElement, LineElement,
    BarElement, ArcElement, Title, ChartTooltip, Legend, Filler
);

const API_BASE = '';

const EMOTION_COLORS = {
    happy: '#4caf50', neutral: '#2196f3', sad: '#9c27b0',
    angry: '#f44336', surprised: '#ff9800', fearful: '#795548', disgusted: '#607d8b'
};

const engagementColor = (score) => {
    if (score >= 0.7) return '#4caf50';
    if (score >= 0.4) return '#ff9800';
    return '#f44336';
};

const engagementLabel = (score) => {
    if (score >= 0.7) return { label: 'High', color: 'success' };
    if (score >= 0.4) return { label: 'Medium', color: 'warning' };
    return { label: 'Low', color: 'error' };
};

const StatCard = ({ icon, label, value, sub, color }) => (
    <Card sx={{ height: '100%' }}>
        <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Avatar sx={{ bgcolor: color + '22', color }}>{icon}</Avatar>
                <Typography variant="body2" color="text.secondary">{label}</Typography>
            </Box>
            <Typography variant="h4" fontWeight="bold" color={color}>{value}</Typography>
            {sub && <Typography variant="caption" color="text.secondary">{sub}</Typography>}
        </CardContent>
    </Card>
);

const InstructorDashboard = () => {
    const [sessionId, setSessionId] = useState('');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [autoRefresh, setAutoRefresh] = useState(false);

    const fetchData = useCallback(async (id) => {
        const target = id || sessionId;
        if (!target.trim()) return;
        setLoading(true);
        setError('');
        try {
            const res = await fetch(`${API_BASE}/engagement/session/${target}/detailed`);
            const json = await res.json();
            if (json.message) { setError(json.message); setData(null); }
            else setData(json);
        } catch {
            setError('Cannot connect to backend. Make sure it is running on port 8000.');
        } finally {
            setLoading(false);
        }
    }, [sessionId]);

    useEffect(() => {
        if (!autoRefresh) return;
        const interval = setInterval(() => fetchData(), 10000);
        return () => clearInterval(interval);
    }, [autoRefresh, fetchData]);

    // Chart data builders
    const timelineChart = data ? {
        labels: data.engagement_timeline.map(p => p.time),
        datasets: [{
            label: 'Avg Engagement',
            data: data.engagement_timeline.map(p => +(p.avg * 100).toFixed(1)),
            borderColor: '#1976d2',
            backgroundColor: 'rgba(25,118,210,0.1)',
            fill: true,
            tension: 0.4,
            pointRadius: 4,
        }]
    } : null;

    const studentBarChart = data ? {
        labels: data.students.map(s => s.student_id),
        datasets: [{
            label: 'Avg Engagement %',
            data: data.students.map(s => +(s.avg_engagement * 100).toFixed(1)),
            backgroundColor: data.students.map(s => engagementColor(s.avg_engagement) + 'cc'),
            borderColor: data.students.map(s => engagementColor(s.avg_engagement)),
            borderWidth: 2,
            borderRadius: 6,
        }]
    } : null;

    const emotionChart = data && Object.keys(data.emotion_distribution).length ? {
        labels: Object.keys(data.emotion_distribution),
        datasets: [{
            data: Object.values(data.emotion_distribution),
            backgroundColor: Object.keys(data.emotion_distribution).map(
                e => EMOTION_COLORS[e] || '#90a4ae'
            ),
            borderWidth: 2,
        }]
    } : null;

    const chartOptions = (title, yLabel = '%') => ({
        responsive: true,
        plugins: {
            legend: { display: false },
            title: { display: true, text: title, font: { size: 14 } },
        },
        scales: {
            y: { beginAtZero: true, max: 100, ticks: { callback: v => v + yLabel } }
        }
    });

    return (
        <Box sx={{ p: 2 }}>
            <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Dashboard color="primary" /> Instructor Dashboard
            </Typography>

            {/* Search bar */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
                        <TextField
                            label="Session ID"
                            value={sessionId}
                            onChange={e => setSessionId(e.target.value)}
                            placeholder="e.g. SESSION_001"
                            size="small"
                            sx={{ flexGrow: 1, minWidth: 200 }}
                            onKeyDown={e => e.key === 'Enter' && fetchData()}
                        />
                        <Button variant="contained" onClick={() => fetchData()} disabled={loading || !sessionId.trim()} startIcon={<Search />}>
                            {loading ? 'Loading...' : 'Load Session'}
                        </Button>
                        <Tooltip title={autoRefresh ? 'Auto-refresh ON (10s)' : 'Enable auto-refresh'}>
                            <Button
                                variant={autoRefresh ? 'contained' : 'outlined'}
                                color={autoRefresh ? 'success' : 'inherit'}
                                onClick={() => setAutoRefresh(v => !v)}
                                startIcon={<Refresh />}
                                disabled={!data}
                            >
                                {autoRefresh ? 'Live' : 'Auto Refresh'}
                            </Button>
                        </Tooltip>
                    </Box>
                </CardContent>
            </Card>

            {loading && <LinearProgress sx={{ mb: 2 }} />}
            {error && <Alert severity="warning" sx={{ mb: 2 }}>{error}</Alert>}

            {!data && !error && (
                <Alert severity="info">
                    Enter a session ID to load the dashboard. Sample session: <strong>SESSION_001</strong>
                </Alert>
            )}

            {data && (
                <>
                    {/* Stat cards */}
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                        <Grid item xs={6} sm={3}>
                            <StatCard icon={<People />} label="Total Students" value={data.total_students} color="#1976d2" />
                        </Grid>
                        <Grid item xs={6} sm={3}>
                            <StatCard
                                icon={<TrendingUp />}
                                label="Avg Engagement"
                                value={`${(data.avg_engagement * 100).toFixed(1)}%`}
                                sub="across all students"
                                color={engagementColor(data.avg_engagement)}
                            />
                        </Grid>
                        <Grid item xs={6} sm={3}>
                            <StatCard icon={<Visibility />} label="High Engagement" value={`${data.high_engagement_pct}%`} sub="≥ 70% score" color="#4caf50" />
                        </Grid>
                        <Grid item xs={6} sm={3}>
                            <StatCard icon={<TrendingDown />} label="Low Engagement" value={`${data.low_engagement_pct}%`} sub="< 40% score" color="#f44336" />
                        </Grid>
                    </Grid>

                    {/* Charts row */}
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                        <Grid item xs={12} md={8}>
                            <Card>
                                <CardContent>
                                    {timelineChart && (
                                        <Line data={timelineChart} options={chartOptions('Engagement Over Time')} height={80} />
                                    )}
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <Card sx={{ height: '100%' }}>
                                <CardContent>
                                    {emotionChart ? (
                                        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                                            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>Emotion Distribution</Typography>
                                            <Doughnut data={emotionChart} options={{ plugins: { legend: { position: 'bottom' } } }} />
                                        </Box>
                                    ) : (
                                        <Typography color="text.secondary" variant="body2">No emotion data available</Typography>
                                    )}
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>

                    {/* Per-student bar chart */}
                    <Card sx={{ mb: 3 }}>
                        <CardContent>
                            {studentBarChart && (
                                <Bar data={studentBarChart} options={chartOptions('Per-Student Engagement')} height={60} />
                            )}
                        </CardContent>
                    </Card>

                    {/* Per-student table */}
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Psychology color="primary" /> Student Breakdown
                            </Typography>
                            <TableContainer component={Paper} variant="outlined">
                                <Table size="small">
                                    <TableHead>
                                        <TableRow sx={{ bgcolor: 'grey.50' }}>
                                            <TableCell><strong>Student ID</strong></TableCell>
                                            <TableCell><strong>Avg Engagement</strong></TableCell>
                                            <TableCell><strong>Gaze Score</strong></TableCell>
                                            <TableCell><strong>Dominant Emotion</strong></TableCell>
                                            <TableCell><strong>Data Points</strong></TableCell>
                                            <TableCell><strong>Status</strong></TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {data.students.sort((a, b) => b.avg_engagement - a.avg_engagement).map((s, i) => {
                                            const { label, color } = engagementLabel(s.avg_engagement);
                                            return (
                                                <TableRow key={i} hover>
                                                    <TableCell>
                                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                            <Avatar sx={{ width: 28, height: 28, fontSize: 12, bgcolor: engagementColor(s.avg_engagement) }}>
                                                                {s.student_id[0]?.toUpperCase()}
                                                            </Avatar>
                                                            {s.student_id}
                                                        </Box>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                            <LinearProgress
                                                                variant="determinate"
                                                                value={s.avg_engagement * 100}
                                                                sx={{
                                                                    width: 80, height: 8, borderRadius: 4,
                                                                    '& .MuiLinearProgress-bar': { bgcolor: engagementColor(s.avg_engagement) }
                                                                }}
                                                            />
                                                            <Typography variant="body2">{(s.avg_engagement * 100).toFixed(1)}%</Typography>
                                                        </Box>
                                                    </TableCell>
                                                    <TableCell>{(s.avg_gaze * 100).toFixed(1)}%</TableCell>
                                                    <TableCell>
                                                        <Chip
                                                            size="small"
                                                            label={s.dominant_emotion || 'N/A'}
                                                            sx={{
                                                                bgcolor: (EMOTION_COLORS[s.dominant_emotion] || '#90a4ae') + '33',
                                                                color: EMOTION_COLORS[s.dominant_emotion] || '#607d8b'
                                                            }}
                                                        />
                                                    </TableCell>
                                                    <TableCell>{s.data_points}</TableCell>
                                                    <TableCell><Chip size="small" label={label} color={color} /></TableCell>
                                                </TableRow>
                                            );
                                        })}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        </CardContent>
                    </Card>
                </>
            )}
        </Box>
    );
};

export default InstructorDashboard;
