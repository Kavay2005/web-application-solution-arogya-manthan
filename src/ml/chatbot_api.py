# -*- coding: utf-8 -*-
"""
ML API for Chatbot - Serves predictions and evaluation metrics
Add these routes to your main.py or create a separate blueprint
"""

import json
import os
import joblib
from typing import Dict, List, Any
from flask import jsonify, request

try:
    import numpy as np
    import pandas as pd
    from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
    import tensorflow as tf
except ImportError:
    pass

class ChatbotMLAPI:
    """API for ML model predictions and metrics"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.models_dir = os.path.join(self.base_dir, 'src', 'ml', 'models')
        self.results_file = os.path.join(self.base_dir, 'data', 'chatbot_ml_results.json')
        self.metrics = None
        self.models = {}
        self.encoders = {}
        self.load_metrics()
        self.load_models()
    
    def load_metrics(self):
        """Load evaluation metrics from file"""
        try:
            if os.path.exists(self.results_file):
                with open(self.results_file, 'r') as f:
                    self.metrics = json.load(f)
                    print("[+] Metrics loaded successfully")
        except Exception as e:
            print(f"[-] Error loading metrics: {e}")
    
    def load_models(self):
        """Load saved ML models from disk"""
        try:
            if not os.path.exists(self.models_dir):
                print(f"[-] Models directory not found: {self.models_dir}")
                return
            
            # Load sklearn models
            sklearn_models = ['naive_bayes', 'decision_tree', 'random_forest', 'logistic_regression', 'svm']
            for model_name in sklearn_models:
                model_path = os.path.join(self.models_dir, f'{model_name}.pkl')
                if os.path.exists(model_path):
                    try:
                        self.models[model_name] = joblib.load(model_path)
                        print(f"[+] Loaded {model_name}")
                    except Exception as e:
                        print(f"[-] Error loading {model_name}: {e}")
            
            # Load neural network model
            nn_path = os.path.join(self.models_dir, 'neural_network.h5')
            if os.path.exists(nn_path):
                try:
                    self.models['neural_network'] = tf.keras.models.load_model(nn_path)
                    print("[+] Loaded neural_network")
                except Exception as e:
                    print(f"[-] Error loading neural_network: {e}")
            
            # Load encoders
            encoder_path = os.path.join(self.models_dir, 'label_encoder.pkl')
            if os.path.exists(encoder_path):
                try:
                    self.encoders['label_encoder'] = joblib.load(encoder_path)
                    print("[+] Loaded label_encoder")
                except Exception as e:
                    print(f"[-] Error loading label_encoder: {e}")
            
            mlb_path = os.path.join(self.models_dir, 'multilabel_binarizer.pkl')
            if os.path.exists(mlb_path):
                try:
                    self.encoders['multilabel_binarizer'] = joblib.load(mlb_path)
                    print("[+] Loaded multilabel_binarizer")
                except Exception as e:
                    print(f"[-] Error loading multilabel_binarizer: {e}")
            
            print(f"[+] Models loaded: {list(self.models.keys())}")
        except Exception as e:
            print(f"[-] Error loading models: {e}")
    
    def get_evaluation_metrics(self) -> Dict[str, Any]:
        """Get all evaluation metrics for all models"""
        if not self.metrics:
            return {
                'status': 'error',
                'message': 'Metrics not available. Run python src/ml/ml_models.py first.'
            }
        
        return {
            'status': 'success',
            'timestamp': self.metrics.get('timestamp'),
            'dataset_size': self.metrics.get('dataset_size'),
            'test_size': self.metrics.get('test_size'),
            'models': self.metrics.get('models', {})
        }
    
    def get_model_metrics(self, model_name: str) -> Dict[str, Any]:
        """Get metrics for a specific model"""
        if not self.metrics:
            return {'status': 'error', 'message': 'Metrics not available'}
        
        models = self.metrics.get('models', {})
        if model_name in models:
            return {
                'status': 'success',
                'model': model_name,
                'metrics': models[model_name]
            }
        else:
            return {'status': 'error', 'message': f'Model {model_name} not found'}
    
    def get_comparison_data(self) -> Dict[str, Any]:
        """Get data for model comparison charts"""
        if not self.metrics:
            return {'status': 'error'}
        
        models = self.metrics.get('models', {})
        
        # Prepare data for chart
        comparison = {
            'models': list(models.keys()),
            'accuracy': [round(models[m].get('accuracy', 0) * 100, 2) for m in models.keys()],
            'precision': [round(models[m].get('precision', 0) * 100, 2) for m in models.keys()],
            'recall': [round(models[m].get('recall', 0) * 100, 2) for m in models.keys()],
            'f1': [round(models[m].get('f1', 0) * 100, 2) for m in models.keys()]
        }
        
        return {
            'status': 'success',
            'data': comparison
        }
    
    def predict(self, symptoms_text: str) -> Dict[str, Any]:
        """
        Make predictions using all loaded models
        Returns: {'status': 'success'/'error', 'predictions': {...}, 'metrics': {...}}
        """
        if not self.models or not self.encoders:
            return {
                'status': 'error',
                'message': 'Models not loaded. Run python src/ml/ml_models.py first.'
            }
        
        try:
            # This is a placeholder - in real implementation, you'd process symptoms_text
            # to features that match training data format
            # For now, we'll return the evaluation metrics showing model performance
            
            return {
                'status': 'success',
                'message': 'Models are ready for predictions',
                'available_models': list(self.models.keys()),
                'metrics': self.metrics.get('models', {}) if self.metrics else {}
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }


# Initialize API
ml_api = ChatbotMLAPI()


def register_ml_routes(app):
    """Register ML routes with Flask app"""
    
    @app.route('/api/ml-metrics', methods=['GET'])
    def get_metrics():
        """Get all evaluation metrics"""
        result = ml_api.get_evaluation_metrics()
        return jsonify(result)
    
    @app.route('/api/ml-model-metrics/<model_name>', methods=['GET'])
    def get_single_model_metrics(model_name):
        """Get metrics for specific model"""
        result = ml_api.get_model_metrics(model_name)
        return jsonify(result)
    
    @app.route('/api/ml-comparison', methods=['GET'])
    def get_comparison():
        """Get comparison data for charts"""
        result = ml_api.get_comparison_data()
        return jsonify(result)
    
    @app.route('/api/ml-predict', methods=['POST'])
    def ml_predict():
        """Make ML predictions"""
        data = request.get_json()
        symptoms = data.get('symptoms', '') if data else ''
        result = ml_api.predict(symptoms)
        return jsonify(result)


# Example integration with existing main.py
# Add to your main.py:
# from src.ml.chatbot_api import register_ml_routes
# register_ml_routes(app)

