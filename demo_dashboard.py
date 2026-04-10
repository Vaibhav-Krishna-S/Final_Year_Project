"""
Standalone  Dashboard with Sample Data
Run this file to see all features of the Student Engagement Analysis Tool
"""
import dash
from dash import dcc, html, Input, Output, callback, dash_table
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Generate sample data
def generate_sample_data():
    """Generate realistic  engagement data"""
    np.random.seed(42)
    
    # Sample students
    students = ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Emma Brown', 
               'Frank Miller', 'Grace Lee', 'Henry Taylor', 'Ivy Chen', 'Jack Anderson']
    
    # Sample sessions
    sessions = [
        {'id': 'session_001', 'name': 'Introduction to Machine Learning', 'course': 'CS 4820'},
        {'id': 'session_002', 'name': 'Deep Learning Fundamentals', 'course': 'CS 4820'},
        {'id': 'session_003', 'name': 'Computer Vision Applications', 'course': 'CS 4820'},
        {'id': 'session_004', 'name': 'Natural Language Processing', 'course': 'CS 4820'}
    ]
    
    # Generate engagement records
    records = []
    emotions = ['happy', 'neutral', 'focused', 'confused', 'bored', 'surprised']
    
    for session in sessions:
        session_start = datetime.now() - timedelta(days=random.randint(1, 30))
        
        for student in students:
            # Generate 50-100 data points per student per session
            num_points = random.randint(50, 100)
            
            for i in range(num_points):
                timestamp = session_start + timedelta(minutes=i*2)
                
                # Simulate realistic engagement patterns
                base_engagement = random.uniform(0.4, 0.9)
                time_factor = 1 - (i / num_points) * 0.3  # Engagement decreases over time
                noise = random.uniform(-0.1, 0.1)
                
                engagement_score = max(0, min(1, base_engagement * time_factor + noise))
                
                records.append({
                    'timestamp': timestamp,
                    'student_name': student,
                    'session_id': session['id'],
                    'session_name': session['name'],
                    'course': session['course'],
                    'engagement_score': engagement_score,
                    'gaze_score': random.uniform(0.3, 0.95),
                    'emotion_score': random.uniform(0.4, 0.9),
                    'presence_score': random.choice([0, 1]) if random.random() > 0.1 else 1,
                    'posture_score': random.uniform(0.5, 0.9),
                    'dominant_emotion': random.choice(emotions),
                    'face_detected': random.choice([True, False]) if random.random() > 0.15 else True,
                    'attention_level': 'High' if engagement_score > 0.7 else 'Medium' if engagement_score > 0.4 else 'Low'
                })
    
    return pd.DataFrame(records)

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Student Engagement Analysis - Dashboard"

# Generate sample data
df = generate_sample_data()

# Define the layout
app.layout = html.Div([
    html.Div([
        html.H1("Student Engagement Analysis Dashboard", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 20}),
        html.H3(" Version with Data", 
                style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': 30}),
        
        html.Div([
            html.Div([
                html.Label("Select Session:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='session-dropdown',
                    options=[{'label': f"{row['course']} - {row['session_name']}", 'value': row['session_id']} 
                            for _, row in df[['session_id', 'session_name', 'course']].drop_duplicates().iterrows()],
                    value=df['session_id'].iloc[0],
                    style={'marginBottom': 10}
                )
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                html.Label("Select Student:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='student-dropdown',
                    options=[{'label': name, 'value': name} for name in sorted(df['student_name'].unique())],
                    value=None,
                    placeholder="All Students"
                )
            ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
        ], style={'marginBottom': 30}),
        
        # Auto-refresh simulation
        dcc.Interval(
            id='interval-component',
            interval=5*1000,  # Update every 5 seconds
            n_intervals=0
        ),
        
        # Summary cards
        html.Div(id='summary-cards', style={'marginBottom': 30}),
        
        # Main charts
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
        
        # Additional analytics
        html.Div([
            html.Div([
                dcc.Graph(id='student-comparison')
            ], style={'width': '50%', 'display': 'inline-block'}),
            
            html.Div([
                dcc.Graph(id='session-trends')
            ], style={'width': '50%', 'display': 'inline-block'})
        ], style={'marginTop': 20}),
        
        # Student performance table
        html.Div([
            html.H3("Student Performance Summary", style={'color': '#2c3e50'}),
            html.Div(id='student-table')
        ], style={'marginTop': 30}),
        
        # AI Insights section
        html.Div([
            html.H3("AI-Generated Insights", style={'color': '#2c3e50'}),
            html.Div(id='ai-insights', style={
                'backgroundColor': '#f8f9fa', 
                'padding': 20, 
                'borderRadius': 10,
                'border': '1px solid #dee2e6'
            })
        ], style={'marginTop': 30}),
        
        # Footer
        html.Div([
            html.Hr(),
            html.P("Student Engagement Analysis Tool - Powered by Computer Vision & AI", 
                   style={'textAlign': 'center', 'color': '#7f8c8d', 'marginTop': 20})
        ])
        
    ], style={'padding': 20, 'maxWidth': '1400px', 'margin': '0 auto'})
])

# Callbacks
@app.callback(
    Output('student-dropdown', 'options'),
    Input('session-dropdown', 'value')
)
def update_student_options(session_id):
    if session_id:
        students = df[df['session_id'] == session_id]['student_name'].unique()
        return [{'label': name, 'value': name} for name in sorted(students)]
    return []

@app.callback(
    [Output('summary-cards', 'children'),
     Output('engagement-timeline', 'figure'),
     Output('engagement-distribution', 'figure'),
     Output('emotion-analysis', 'figure'),
     Output('attention-heatmap', 'figure'),
     Output('student-comparison', 'figure'),
     Output('session-trends', 'figure'),
     Output('student-table', 'children'),
     Output('ai-insights', 'children')],
    [Input('session-dropdown', 'value'),
     Input('student-dropdown', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_dashboard(session_id, student_name, n):
    # Filter data
    filtered_df = df[df['session_id'] == session_id] if session_id else df
    if student_name:
        filtered_df = filtered_df[filtered_df['student_name'] == student_name]
    
    if filtered_df.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return [], empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, [], []
    
    # Summary metrics
    avg_engagement = filtered_df['engagement_score'].mean()
    total_students = filtered_df['student_name'].nunique()
    total_records = len(filtered_df)
    attention_rate = filtered_df['face_detected'].mean()
    
    # Summary cards
    summary_cards = html.Div([
        html.Div([
            html.H2(f"{avg_engagement:.1%}", style={'margin': 0, 'color': '#3498db'}),
            html.P("Average Engagement", style={'margin': 0, 'fontSize': 14})
        ], className='summary-card', style={'textAlign': 'center', 'padding': 20, 'backgroundColor': '#ecf0f1', 
             'borderRadius': 10, 'width': '22%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H2(f"{total_students}", style={'margin': 0, 'color': '#e74c3c'}),
            html.P("Active Students", style={'margin': 0, 'fontSize': 14})
        ], className='summary-card', style={'textAlign': 'center', 'padding': 20, 'backgroundColor': '#ecf0f1', 
             'borderRadius': 10, 'width': '22%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H2(f"{total_records:,}", style={'margin': 0, 'color': '#f39c12'}),
            html.P("Data Points", style={'margin': 0, 'fontSize': 14})
        ], className='summary-card', style={'textAlign': 'center', 'padding': 20, 'backgroundColor': '#ecf0f1', 
             'borderRadius': 10, 'width': '22%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H2(f"{attention_rate:.1%}", style={'margin': 0, 'color': '#27ae60'}),
            html.P("Attention Rate", style={'margin': 0, 'fontSize': 14})
        ], className='summary-card', style={'textAlign': 'center', 'padding': 20, 'backgroundColor': '#ecf0f1', 
             'borderRadius': 10, 'width': '22%', 'display': 'inline-block', 'margin': '1%'})
    ])
    
    # 1. Engagement Timeline
    timeline_fig = px.line(filtered_df, x='timestamp', y='engagement_score', 
                          color='student_name' if not student_name else None,
                          title='Real-time Engagement Timeline')
    timeline_fig.update_layout(yaxis_title='Engagement Score', xaxis_title='Time')
    
    # 2. Engagement Distribution
    dist_fig = px.histogram(filtered_df, x='engagement_score', nbins=20, 
                           title='Engagement Score Distribution')
    dist_fig.update_layout(xaxis_title='Engagement Score', yaxis_title='Frequency')
    
    # 3. Emotion Analysis
    emotion_counts = filtered_df['dominant_emotion'].value_counts()
    emotion_fig = px.pie(values=emotion_counts.values, names=emotion_counts.index,
                        title='Emotion Distribution')
    
    # 4. Attention Heatmap
    if len(filtered_df) > 20 and total_students > 1:
        filtered_df['time_bin'] = pd.cut(range(len(filtered_df)), bins=10, labels=False)
        heatmap_data = filtered_df.groupby(['student_name', 'time_bin'])['engagement_score'].mean().reset_index()
        heatmap_pivot = heatmap_data.pivot(index='student_name', columns='time_bin', values='engagement_score')
        
        heatmap_fig = px.imshow(heatmap_pivot, title='Student Engagement Heatmap',
                               labels=dict(x="Time Period", y="Student", color="Engagement"))
    else:
        heatmap_fig = go.Figure()
        heatmap_fig.add_annotation(text="Heatmap requires more data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
    
    # 5. Student Comparison
    student_avg = filtered_df.groupby('student_name')['engagement_score'].mean().sort_values(ascending=True)
    comparison_fig = px.bar(x=student_avg.values, y=student_avg.index, orientation='h',
                           title='Student Engagement Comparison')
    comparison_fig.update_layout(xaxis_title='Average Engagement Score', yaxis_title='Student')
    
    # 6. Session Trends
    session_trends = df.groupby(['session_name', 'course'])['engagement_score'].mean().reset_index()
    trends_fig = px.bar(session_trends, x='session_name', y='engagement_score', color='course',
                       title='Session Performance Trends')
    trends_fig.update_layout(xaxis_title='Session', yaxis_title='Average Engagement')
    
    # 7. Student Performance Table
    student_stats = filtered_df.groupby('student_name').agg({
        'engagement_score': ['mean', 'std', 'count'],
        'face_detected': 'mean',
        'gaze_score': 'mean',
        'emotion_score': 'mean'
    }).round(3)
    
    table_data = []
    for student in student_stats.index:
        table_data.append({
            'Student': student,
            'Avg Engagement': f"{student_stats.loc[student, ('engagement_score', 'mean')]:.3f}",
            'Std Dev': f"{student_stats.loc[student, ('engagement_score', 'std')]:.3f}",
            'Data Points': f"{student_stats.loc[student, ('engagement_score', 'count')]}",
            'Attention Rate': f"{student_stats.loc[student, ('face_detected', 'mean')]:.3f}",
            'Avg Gaze Score': f"{student_stats.loc[student, ('gaze_score', 'mean')]:.3f}",
            'Avg Emotion Score': f"{student_stats.loc[student, ('emotion_score', 'mean')]:.3f}"
        })
    
    table = dash_table.DataTable(
        data=table_data,
        columns=[{"name": col, "id": col} for col in table_data[0].keys() if table_data],
        style_cell={'textAlign': 'center', 'padding': '10px'},
        style_header={'backgroundColor': '#3498db', 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f8f9fa'
            }
        ]
    )
    
    # 8. AI Insights
    insights = html.Div([
        html.H4("Session Analysis", style={'color': '#2c3e50'}),
        html.P(f"• Overall engagement level: {'High' if avg_engagement > 0.7 else 'Medium' if avg_engagement > 0.5 else 'Low'} ({avg_engagement:.1%})"),
        html.P(f"• Most engaged student: {student_avg.index[-1]} ({student_avg.iloc[-1]:.1%})"),
        html.P(f"• Attention consistency: {attention_rate:.1%} of time with face detected"),
        html.P(f"• Dominant emotion: {emotion_counts.index[0]} ({emotion_counts.iloc[0]} occurrences)"),
        html.Hr(),
        html.H4("Recommendations", style={'color': '#2c3e50'}),
        html.P("• Consider interactive elements to boost engagement during low periods"),
        html.P("• Monitor students with consistently low engagement scores"),
        html.P("• Schedule breaks when attention rates drop below 70%"),
        html.P("• Use positive emotions data to identify effective teaching moments")
    ])
    
    return summary_cards, timeline_fig, dist_fig, emotion_fig, heatmap_fig, comparison_fig, trends_fig, table, insights

if __name__ == '__main__':
    print("Starting Student Engagement Analysis ...")
    print("Dashboard will be available at: http://localhost:8050")
    print("Data refreshes every 5 seconds to simulate real-time updates")
    print("Features: Real-time analytics, AI insights, student comparison, emotion analysis")
    
    app.run(debug=True, port=8050, host='0.0.0.0')