# -*- coding: utf-8 -*-
"""
ML API Module - Simple interface for chatbot to use saved ML models
Use this in your Flask/FastAPI backend
"""

from typing import Dict, List, Any
from src.ml.evaluation_service import get_evaluation_service


class ChatbotMLAPI:
    """Simple API for chatbot to use saved ML models"""
    
    def __init__(self):
        """Initialize with saved models"""
        self.service = get_evaluation_service()
    
    def is_available(self) -> bool:
        """Check if ML models are available"""
        return self.service.is_ready()
    
    def diagnose(self, symptoms: List[str], user_id: str = None) -> Dict[str, Any]:
        """
        Diagnose using saved ML models
        
        Args:
            symptoms: List of symptoms
            user_id: Optional user identifier
        
        Returns:
            {
                'disease': predicted disease,
                'confidence': 0.0-1.0,
                'consensus': percentage of models agreeing,
                'status': 'success' or 'error'
            }
        """
        
        if not self.is_available():
            return {
                'status': 'error',
                'message': 'ML models not available. Run setup_ml_once.py first.'
            }
        
        # Get evaluation
        result = self.service.evaluate_symptoms(symptoms, user_id=user_id)
        
        if result.get('status') == 'success':
            return {
                'status': 'success',
                'disease': result['predicted_disease'],
                'confidence': result['confidence'],
                'consensus': result['consensus'],
                'model_count': result['total_models'],
                'models_agree': result['vote_count']
            }
        else:
            return {
                'status': 'error',
                'message': result.get('error', 'Evaluation failed')
            }
    
    def get_confidence_label(self, confidence: float) -> str:
        """Get human-readable confidence label"""
        if confidence >= 0.9:
            return "Very High"
        elif confidence >= 0.8:
            return "High"
        elif confidence >= 0.7:
            return "Medium"
        elif confidence >= 0.6:
            return "Low"
        else:
            return "Very Low"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get pre-trained model metrics"""
        metrics = self.service.get_model_metrics()
        
        if metrics:
            return {
                'status': 'success',
                'best_model': metrics['best_model'],
                'best_accuracy': metrics['best_accuracy'],
                'total_models': len(metrics['all_models']),
                'dataset_size': metrics['dataset_info'],
                'models': metrics['all_models']
            }
        else:
            return {
                'status': 'error',
                'message': 'Metrics not available'
            }
    
    def get_results_summary(self) -> Dict[str, Any]:
        """Get summary of evaluations"""
        summary = self.service.get_results_summary()
        return {
            'total_evaluations': summary['total_evaluations'],
            'successful': summary['successful'],
            'failed': summary['failed'],
            'results_file': summary['results_file']
        }


# Create singleton instance
_ml_api = None

def get_ml_api() -> ChatbotMLAPI:
    """Get singleton ML API instance"""
    global _ml_api
    if _ml_api is None:
        _ml_api = ChatbotMLAPI()
    return _ml_api


# Example usage with Flask
if __name__ == "__main__":
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    ml_api = get_ml_api()
    
    @app.route('/api/diagnose', methods=['POST'])
    def diagnose():
        """
        POST /api/diagnose
        Body: {"symptoms": ["fever", "cough"]}
        Returns: {"disease": "Cold", "confidence": 0.87, ...}
        """
        data = request.json or {}
        symptoms = data.get('symptoms', [])
        user_id = data.get('user_id', None)
        
        result = ml_api.diagnose(symptoms, user_id)
        
        if result['status'] == 'success':
            result['confidence_label'] = ml_api.get_confidence_label(result['confidence'])
        
        return jsonify(result)
    
    @app.route('/api/ml-metrics', methods=['GET'])
    def get_metrics():
        """
        GET /api/ml-metrics
        Returns: Model evaluation metrics
        """
        return jsonify(ml_api.get_metrics())
    
    @app.route('/api/ml-status', methods=['GET'])
    def get_status():
        """
        GET /api/ml-status
        Returns: Whether ML models are available
        """
        return jsonify({
            'available': ml_api.is_available(),
            'message': 'ML models ready' if ml_api.is_available() else 'Run setup_ml_once.py'
        })
    
    # Run server
    print("\n[+] ML API Server running on http://localhost:5000")
    print("[+] Available endpoints:")
    print("    POST /api/diagnose - Diagnose symptoms")
    print("    GET  /api/ml-metrics - Get model metrics")
    print("    GET  /api/ml-status - Check if ready\n")
    
    app.run(debug=True, port=5000)
