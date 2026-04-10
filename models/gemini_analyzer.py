"""
Gemini AI integration for engagement analysis and feedback generation
"""
import google.generativeai as genai
from typing import Dict, Any, List, Optional
import json
import logging
from backend.config import settings

logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    """Gemini AI analyzer for engagement insights and feedback"""
    
    def __init__(self):
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here":
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            self.enabled = True
        else:
            self.model = None
            self.enabled = False
            logger.warning("Gemini API key not configured - AI insights disabled")
    
    def generate_session_summary(self, engagement_data: List[Dict[str, Any]]) -> str:
        """Generate AI-powered session summary"""
        if not self.enabled:
            return self._fallback_summary(engagement_data)
        
        try:
            # Prepare data for analysis
            summary_stats = self._calculate_stats(engagement_data)
            
            prompt = f"""
            Analyze this class engagement data and provide a concise summary:
            
            Session Statistics:
            - Average Engagement: {summary_stats['avg_engagement']:.1%}
            - Total Students: {summary_stats['total_students']}
            - Attention Rate: {summary_stats['attention_rate']:.1%}
            - Duration: {summary_stats['duration_minutes']} minutes
            - Top Emotions: {', '.join(summary_stats['top_emotions'])}
            
            Provide a brief 2-3 sentence summary focusing on:
            1. Overall class engagement level
            2. Key observations about student attention
            3. One actionable recommendation for the instructor
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return self._fallback_summary(engagement_data)
    
    def generate_student_feedback(self, student_data: List[Dict[str, Any]]) -> str:
        """Generate personalized student feedback"""
        if not self.enabled:
            return "Keep up the good work! Stay engaged during class."
        
        try:
            stats = self._calculate_student_stats(student_data)
            
            prompt = f"""
            Generate encouraging feedback for a student based on their engagement data:
            
            Student Performance:
            - Average Engagement: {stats['avg_engagement']:.1%}
            - Attention Consistency: {stats['consistency']:.1%}
            - Most Common Emotion: {stats['dominant_emotion']}
            - Sessions Attended: {stats['session_count']}
            
            Provide 1-2 sentences of positive, constructive feedback that:
            1. Acknowledges their participation
            2. Offers a specific tip for improvement if needed
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Student feedback generation failed: {e}")
            return "Great participation! Keep staying engaged during class sessions."
    
    def analyze_engagement_trends(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze engagement trends over time"""
        if not self.enabled:
            return self._basic_trend_analysis(historical_data)
        
        try:
            trends = self._calculate_trends(historical_data)
            
            prompt = f"""
            Analyze these engagement trends and provide insights:
            
            Trend Data:
            - Engagement Trend: {trends['engagement_slope']:.3f} (positive = improving)
            - Attention Stability: {trends['attention_variance']:.3f}
            - Peak Performance Time: {trends['best_time']}
            - Participation Rate: {trends['participation_rate']:.1%}
            
            Provide a JSON response with:
            {{
                "trend_direction": "improving/stable/declining",
                "key_insight": "brief observation",
                "recommendation": "actionable suggestion"
            }}
            """
            
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return self._basic_trend_analysis(historical_data)
    
    def _calculate_stats(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate basic statistics from engagement data"""
        if not data:
            return {}
        
        engagement_scores = [d['engagement_score'] for d in data if d.get('face_detected')]
        emotions = [d['dominant_emotion'] for d in data if d.get('dominant_emotion')]
        
        return {
            'avg_engagement': sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0,
            'total_students': len(set(d['student_id'] for d in data)),
            'attention_rate': len(engagement_scores) / len(data) if data else 0,
            'duration_minutes': len(data) * 2 / 60,  # Assuming 2-second intervals
            'top_emotions': list(set(emotions))[:3]
        }
    
    def _calculate_student_stats(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate individual student statistics"""
        if not data:
            return {}
        
        engagement_scores = [d['engagement_score'] for d in data if d.get('face_detected')]
        emotions = [d['dominant_emotion'] for d in data if d.get('dominant_emotion')]
        
        return {
            'avg_engagement': sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0,
            'consistency': 1 - (max(engagement_scores) - min(engagement_scores)) if len(engagement_scores) > 1 else 1,
            'dominant_emotion': max(set(emotions), key=emotions.count) if emotions else 'neutral',
            'session_count': len(set(d.get('session_id') for d in data))
        }
    
    def _calculate_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate trend metrics"""
        import numpy as np
        
        if len(data) < 2:
            return {}
        
        engagement_scores = [d['engagement_score'] for d in data if d.get('face_detected')]
        
        # Simple linear trend
        x = list(range(len(engagement_scores)))
        slope = np.polyfit(x, engagement_scores, 1)[0] if len(engagement_scores) > 1 else 0
        
        return {
            'engagement_slope': slope,
            'attention_variance': np.var(engagement_scores) if engagement_scores else 0,
            'best_time': 'mid-session',  # Simplified
            'participation_rate': len(engagement_scores) / len(data) if data else 0
        }
    
    def _fallback_summary(self, data: List[Dict[str, Any]]) -> str:
        """Fallback summary when Gemini is not available"""
        stats = self._calculate_stats(data)
        
        if stats.get('avg_engagement', 0) > 0.7:
            return f"Excellent class engagement with {stats['avg_engagement']:.1%} average attention. Students were highly focused throughout the session."
        elif stats.get('avg_engagement', 0) > 0.5:
            return f"Good class participation with {stats['avg_engagement']:.1%} engagement. Consider interactive activities to boost attention."
        else:
            return f"Class engagement at {stats['avg_engagement']:.1%}. Recommend more interactive content and frequent check-ins."
    
    def _basic_trend_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Basic trend analysis fallback"""
        return {
            "trend_direction": "stable",
            "key_insight": "Consistent engagement patterns observed",
            "recommendation": "Continue current teaching approach"
        }

# Global Gemini analyzer instance
gemini_analyzer = GeminiAnalyzer()