"""
Dashboard application using Plotly Dash for engagement visualization
"""
import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_db_context
from database.models import EngagementRecord, Student, Session

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Student Engagement Dashboard"

# Define the layout
app.layout = html.Div([
    html.Div([
        html.H1("Student Engagement Analysis Dashboard", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
        
        html.Div([
            html.Div([
                html.Label("Select Session:"),
                dcc.Dropdown(
                    id='session-dropdown',
                    options=[],
                    value=None,
                    placeholder="Select a session"
                )
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                html.Label("Select Student:"),
                dcc.Dropdown(
                    id='student-dropdown',
                    options=[],
                    value=None,
                    placeholder="Select a student (optional)"
                )
            ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
        ], style={'marginBottom': 30}),
        
        # Auto-refresh interval
        dcc.Interval(
            id='interval-component',
            interval=10*1000,  # Update every 10 seconds
            n_intervals=0
        ),
        
        # Summary cards
        html.Div(id='summary-cards', style={'marginBottom': 30}),
        
        # Charts
        html.Div([
            html.Div([
                dcc.Graph(id='engagement-timeline')
            ], style={'width': '50%', 'display': 'inline-block'}),
            
            html.Div([
                dcc.Graph(id='engagement-distribution')
            ], style={'width': '50%', 'display': 'inline-block'})
        ]),
        
        html.Div([
            html.Div([
                dcc.Graph(id='emotion-analysis')
            ], style={'width': '50%', 'display': 'inline-block'}),
            
            html.Div([
                dcc.Graph(id='attention-heatmap')
            ], style={'width': '50%', 'display': 'inline-block'})
        ], style={'marginTop': 20}),
        
        # Student comparison table
        html.Div([
            html.H3("Student Engagement Comparison"),
            html.Div(id='student-table')
        ], style={'marginTop': 30})
        
    ], style={'padding': 20})
])

def get_session_data():
    """Get available sessions from database"""
    try:
        with get_db_context() as db:
            sessions = db.query(Session).all()
            return [{'label': f"{s.course_name} - {s.session_name}", 'value': s.id} 
                   for s in sessions]
    except Exception as e:
        print(f"Error getting sessions: {e}")
        return []

def get_student_data(session_id=None):
    """Get available students from database"""
    try:
        with get_db_context() as db:
            query = db.query(Student)
            if session_id:
                query = query.join(EngagementRecord).filter(
                    EngagementRecord.session_id == session_id
                ).distinct()
            students = query.all()
            return [{'label': s.name, 'value': s.id} for s in students]
    except Exception as e:
        print(f"Error getting students: {e}")
        return []

def get_engagement_data(session_id, student_id=None):
    """Get engagement data from database"""
    try:
        with get_db_context() as db:
            query = db.query(EngagementRecord).filter(
                EngagementRecord.session_id == session_id
            )
            if student_id:
                query = query.filter(EngagementRecord.student_id == student_id)
            
            records = query.order_by(EngagementRecord.timestamp).all()
            
            data = []
            for record in records:
                data.append({
                    'timestamp': record.timestamp,
                    'student_id': record.student_id,
                    'engagement_score': record.engagement_score,
                    'gaze_score': record.gaze_score,
                    'emotion_score': record.emotion_score,
                    'presence_score': record.presence_score,
                    'dominant_emotion': record.dominant_emotion,
                    'face_detected': record.face_detected
                })
            
            return pd.DataFrame(data)
    except Exception as e:
        print(f"Error getting engagement data: {e}")
        return pd.DataFrame()

# Callbacks
@app.callback(
    Output('session-dropdown', 'options'),
    Input('interval-component', 'n_intervals')
)
def update_session_options(n):
    return get_session_data()

@app.callback(
    Output('student-dropdown', 'options'),
    Input('session-dropdown', 'value')
)
def update_student_options(session_id):
    if session_id:
        return get_student_data(session_id)
    return []

@app.callback(
    [Output('summary-cards', 'children'),
     Output('engagement-timeline', 'figure'),
     Output('engagement-distribution', 'figure'),
     Output('emotion-analysis', 'figure'),
     Output('attention-heatmap', 'figure'),
     Output('student-table', 'children')],
    [Input('session-dropdown', 'value'),
     Input('student-dropdown', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_dashboard(session_id, student_id, n):
    if not session_id:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="Please select a session", 
                               xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return [], empty_fig, empty_fig, empty_fig, empty_fig, []
    
    df = get_engagement_data(session_id, student_id)
    
    if df.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No data available", 
                               xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return [], empty_fig, empty_fig, empty_fig, empty_fig, []
    
    # Summary cards
    avg_engagement = df['engagement_score'].mean()
    total_students = df['student_id'].nunique()
    total_records = len(df)
    attention_rate = df['face_detected'].mean()
    
    summary_cards = html.Div([
        html.Div([
            html.H4(f"{avg_engagement:.1%}", style={'margin': 0, 'color': '#3498db'}),
            html.P("Average Engagement", style={'margin': 0})
        ], style={'textAlign': 'center', 'padding': 20, 'backgroundColor': '#ecf0f1', 
                 'borderRadius': 10, 'width': '22%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H4(f"{total_students}", style={'margin': 0, 'color': '#e74c3c'}),
            html.P("Active Students", style={'margin': 0})
        ], style={'textAlign': 'center', 'padding': 20, 'backgroundColor': '#ecf0f1', 
                 'borderRadius': 10, 'width': '22%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H4(f"{total_records}", style={'margin': 0, 'color': '#f39c12'}),
            html.P("Data Points", style={'margin': 0})
        ], style={'textAlign': 'center', 'padding': 20, 'backgroundColor': '#ecf0f1', 
                 'borderRadius': 10, 'width': '22%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H4(f"{attention_rate:.1%}", style={'margin': 0, 'color': '#27ae60'}),
            html.P("Attention Rate", style={'margin': 0})
        ], style={'textAlign': 'center', 'padding': 20, 'backgroundColor': '#ecf0f1', 
                 'borderRadius': 10, 'width': '22%', 'display': 'inline-block', 'margin': '1%'})
    ])
    
    # Engagement timeline
    timeline_fig = px.line(df, x='timestamp', y='engagement_score', 
                          color='student_id' if not student_id else None,
                          title='Engagement Over Time')
    timeline_fig.update_layout(yaxis_title='Engagement Score', xaxis_title='Time')
    
    # Engagement distribution
    dist_fig = px.histogram(df, x='engagement_score', nbins=20, 
                           title='Engagement Score Distribution')
    dist_fig.update_layout(xaxis_title='Engagement Score', yaxis_title='Frequency')
    
    # Emotion analysis
    emotion_counts = df['dominant_emotion'].value_counts()
    emotion_fig = px.pie(values=emotion_counts.values, names=emotion_counts.index,
                        title='Emotion Distribution')
    
    # Attention heatmap (simplified)
    if len(df) > 10:
        df['time_bin'] = pd.cut(range(len(df)), bins=10, labels=False)
        heatmap_data = df.groupby(['student_id', 'time_bin'])['engagement_score'].mean().reset_index()
        heatmap_pivot = heatmap_data.pivot(index='student_id', columns='time_bin', values='engagement_score')
        
        heatmap_fig = px.imshow(heatmap_pivot, title='Engagement Heatmap Over Time',
                               labels=dict(x="Time Period", y="Student", color="Engagement"))
    else:
        heatmap_fig = go.Figure()
        heatmap_fig.add_annotation(text="Insufficient data for heatmap", 
                                 xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
    
    # Student comparison table
    student_stats = df.groupby('student_id').agg({
        'engagement_score': ['mean', 'std', 'count'],
        'face_detected': 'mean'
    }).round(3)
    
    table_data = []
    for student in student_stats.index:
        table_data.append(html.Tr([
            html.Td(student),
            html.Td(f"{student_stats.loc[student, ('engagement_score', 'mean')]:.3f}"),
            html.Td(f"{student_stats.loc[student, ('engagement_score', 'std')]:.3f}"),
            html.Td(f"{student_stats.loc[student, ('engagement_score', 'count')]}"),
            html.Td(f"{student_stats.loc[student, ('face_detected', 'mean')]:.3f}")
        ]))
    
    table = html.Table([
        html.Thead([
            html.Tr([
                html.Th('Student ID'),
                html.Th('Avg Engagement'),
                html.Th('Std Dev'),
                html.Th('Data Points'),
                html.Th('Attention Rate')
            ])
        ]),
        html.Tbody(table_data)
    ], style={'width': '100%', 'textAlign': 'center'})
    
    return summary_cards, timeline_fig, dist_fig, emotion_fig, heatmap_fig, table

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)