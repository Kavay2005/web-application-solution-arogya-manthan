# -*- coding: utf-8 -*-
"""
Triage Engine
Determines the urgency level of medical symptoms.
"""

from typing import Dict, Any


class TriageEngine:
    """Determine triage level based on symptoms"""
    
    # Define urgency keywords
    EMERGENCY_KEYWORDS = [
        'chest pain', 'difficulty breathing', 'shortness of breath',
        'severe', 'emergency', 'critical', 'unconscious', 'bleeding',
        'accident', 'poisoning', 'overdose', 'choking'
    ]
    
    URGENT_KEYWORDS = [
        'fever', 'acute', 'sudden', 'severe pain', 'intense',
        'uncontrolled', 'loss of consciousness'
    ]
    
    def __init__(self):
        """Initialize triage engine"""
        pass
    
    def determine_triage_level(self, symptoms: list, transcript: str = "") -> Dict[str, Any]:
        """
        Determine urgency level based on symptoms.
        
        Returns:
            Dict with 'level' and 'reason' keys
            Level can be: 'Emergency', 'Urgent', or 'Standard'
        """
        # Combine symptoms and transcript for analysis
        text = ' '.join(symptoms) + ' ' + transcript
        text_lower = text.lower()
        
        # Check for emergency keywords
        for keyword in self.EMERGENCY_KEYWORDS:
            if keyword in text_lower:
                return {
                    'level': 'Emergency',
                    'reason': f'Critical symptom detected: {keyword}',
                    'priority': 1
                }
        
        # Check for urgent keywords
        for keyword in self.URGENT_KEYWORDS:
            if keyword in text_lower:
                return {
                    'level': 'Urgent',
                    'reason': f'Urgent symptom detected: {keyword}',
                    'priority': 2
                }
        
        # Standard consultation
        return {
            'level': 'Standard',
            'reason': 'Routine consultation recommended',
            'priority': 3
        }
    
    def get_recommendations(self, triage_level: str) -> Dict[str, Any]:
        """Get care recommendations based on triage level"""
        recommendations = {
            'Emergency': {
                'action': 'Call emergency services (911/Ambulance)',
                'description': 'Requires immediate professional medical attention',
                'wait_time': '< 5 minutes'
            },
            'Urgent': {
                'action': 'Visit urgent care center or hospital',
                'description': 'Requires professional medical evaluation within hours',
                'wait_time': '< 2 hours'
            },
            'Standard': {
                'action': 'Schedule appointment with doctor',
                'description': 'Can be handled in routine consultation',
                'wait_time': 'Within 1-2 days'
            }
        }
        
        return recommendations.get(triage_level, recommendations['Standard'])
