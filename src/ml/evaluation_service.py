# -*- coding: utf-8 -*-
"""
ML Evaluation Module - Evaluates user symptoms using saved trained models
Does NOT train - just uses pre-trained models saved locally
"""

import os
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime

class MLEvaluationService:
    """
    Evaluates user symptoms using pre-trained ML models
    Models must be trained first using setup_ml_once.py
    """
    
    def __init__(self):
        """Initialize with pre-trained models"""
        self.ml_integration = None
        self.evaluation_results = []
        self.results_file = None
        
        # Load models
        try:
            from src.ml.chatbot_ml_integration import get_ml_integration
            self.ml_integration = get_ml_integration()
            print("[+] Pre-trained ML models loaded successfully")
        except Exception as e:
            print(f"[-] Error loading pre-trained models: {e}")
            print("[!] Run setup_ml_once.py first to train and save models")
    
    def is_ready(self) -> bool:
        """Check if ML models are available"""
        return self.ml_integration is not None and self.ml_integration.is_models_available()
    
    def evaluate_symptoms(self, symptoms: List[str], user_id: str = "anonymous") -> Dict[str, Any]:
        """
        Evaluate user symptoms using saved ML models
        
        Args:
            symptoms: List of symptoms (e.g., ["fever", "cough"])
            user_id: Optional user identifier
        
        Returns:
            Dictionary with:
            - predicted_disease: Most likely disease
            - confidence: Confidence score (0-1)
            - consensus: Percentage of models agreeing
            - model_predictions: Individual model predictions
        """
        
        if not self.is_ready():
            return {
                'error': 'ML models not available',
                'message': 'Run setup_ml_once.py to train models first'
            }
        
        try:
            # Get ensemble prediction from saved models
            result = self.ml_integration.get_ensemble_prediction(symptoms)
            
            if result:
                # Add metadata
                evaluation = {
                    'timestamp': datetime.now().isoformat(),
                    'user_id': user_id,
                    'symptoms': symptoms,
                    'predicted_disease': result.get('ensemble_prediction'),
                    'confidence': result.get('average_confidence'),
                    'consensus': result.get('consensus'),
                    'vote_count': result.get('vote_count'),
                    'total_models': result.get('total_models'),
                    'model_predictions': result.get('model_predictions'),
                    'status': 'success'
                }
                
                # Save result
                self.evaluation_results.append(evaluation)
                self._save_result(evaluation)
                
                return evaluation
            else:
                return {'error': 'No prediction available', 'status': 'error'}
        
        except Exception as e:
            error_result = {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'status': 'error'
            }
            self._save_result(error_result)
            return error_result
    
    def _save_result(self, result: Dict[str, Any]):
        """Save evaluation result to file"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            results_dir = os.path.join(base_dir, 'data')
            os.makedirs(results_dir, exist_ok=True)
            
            results_file = os.path.join(results_dir, 'user_evaluation_results.jsonl')
            
            # Append result to file (one JSON per line)
            with open(results_file, 'a') as f:
                json.dump(result, f)
                f.write('\n')
            
            self.results_file = results_file
        except Exception as e:
            print(f"[-] Error saving result: {e}")
    
    def get_results_summary(self) -> Dict[str, Any]:
        """Get summary of all evaluations"""
        if not self.evaluation_results:
            return {'total_evaluations': 0, 'results': []}
        
        successful = [r for r in self.evaluation_results if r.get('status') == 'success']
        
        return {
            'total_evaluations': len(self.evaluation_results),
            'successful': len(successful),
            'failed': len(self.evaluation_results) - len(successful),
            'results_file': self.results_file,
            'latest_result': successful[-1] if successful else None
        }
    
    def get_model_metrics(self) -> Dict[str, Any]:
        """Get pre-trained model evaluation metrics"""
        if not self.is_ready():
            return None
        
        try:
            return self.ml_integration.get_evaluation_metrics()
        except Exception as e:
            print(f"[-] Error getting metrics: {e}")
            return None


# Singleton instance
_instance = None

def get_evaluation_service() -> MLEvaluationService:
    """Get singleton instance of evaluation service"""
    global _instance
    if _instance is None:
        _instance = MLEvaluationService()
    return _instance


# Example usage
if __name__ == "__main__":
    print("\n" + "="*70)
    print("ML EVALUATION SERVICE")
    print("="*70 + "\n")
    
    # Get service
    service = get_evaluation_service()
    
    # Check if ready
    if not service.is_ready():
        print("[!] Models not ready. Run setup_ml_once.py first.")
    else:
        print("[+] ML models are ready for evaluation\n")
        
        # Test with sample symptoms
        test_symptoms = [
            ["fever", "cough", "headache"],
            ["chest pain", "shortness of breath"],
            ["nausea", "dizziness", "fatigue"]
        ]
        
        print("[*] Evaluating test symptoms...\n")
        
        for symptoms in test_symptoms:
            print(f"Symptoms: {symptoms}")
            result = service.evaluate_symptoms(symptoms, user_id="test_user")
            
            if result.get('status') == 'success':
                print(f"  → Predicted: {result['predicted_disease']}")
                print(f"  → Confidence: {result['confidence']:.2%}")
                print(f"  → Consensus: {result['consensus']:.1%} of models agree")
            else:
                print(f"  → Error: {result.get('error')}")
            print()
        
        # Show summary
        summary = service.get_results_summary()
        print(f"Summary: {summary['total_evaluations']} evaluations")
        print(f"Success: {summary['successful']}, Failed: {summary['failed']}")
        print(f"Results saved to: {summary['results_file']}\n")
        
        # Show metrics
        metrics = service.get_model_metrics()
        if metrics:
            print(f"Best Model: {metrics['best_model']} ({metrics['best_accuracy']:.1%})")
