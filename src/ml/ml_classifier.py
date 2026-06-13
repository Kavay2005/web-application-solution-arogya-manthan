# -*- coding: utf-8 -*-
"""
Machine Learning Classifier for Disease Prediction
Tests multiple classifiers and compares with rule-based approach.
Tracks evaluation metrics (accuracy, precision, recall, F1, confusion matrix, KDE, KPE).
"""

import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import pickle
import json
from datetime import datetime

# ML Libraries
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report
from scipy.stats import gaussian_kde, entropy

# Add src directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

from nlp.symptom_extractor import SymptomExtractor
from rules.disease_matcher import DiseaseMatcher


class MLClassifier:
    """Machine Learning based disease classification with comparison metrics"""
    
    def __init__(self, symptom_dict: Dict[str, List[str]], kb_dict: Dict[str, Any] = None):
        """Initialize ML classifier with symptom dictionary"""
        self.symptom_dict = symptom_dict or {}
        self.kb_dict = kb_dict or {}
        self.mlb = MultiLabelBinarizer()
        self.models = {}
        self.model_performance = {}
        self.evaluation_metrics = {}
        self.last_query_metrics = None
        
        # Get all unique symptoms
        self.all_symptoms = self._extract_all_symptoms()
        self.diseases = list(symptom_dict.keys())
        
        # Initialize models
        self._initialize_models()
        
        # Train models
        self._train_models()
    
    def _extract_all_symptoms(self) -> List[str]:
        """Extract all unique symptoms from symptom dictionary"""
        all_symptoms = set()
        for symptoms in self.symptom_dict.values():
            all_symptoms.update(symptoms)
        return sorted(list(all_symptoms))
    
    def _initialize_models(self):
        """Initialize multiple ML models"""
        self.models = {
            'SVM': SVC(kernel='rbf', probability=True, random_state=42),
            'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
            'NaiveBayes': GaussianNB(),
            'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1),
            'KNN': KNeighborsClassifier(n_neighbors=5, n_jobs=-1)
        }
    
    def _train_models(self):
        """Train all models using the symptom data"""
        try:
            # Prepare training data
            X_train = []
            y_train = []
            
            for disease, symptoms in self.symptom_dict.items():
                # Create binary vector for this disease's symptoms
                symptom_vector = self._create_symptom_vector(symptoms)
                X_train.append(symptom_vector)
                y_train.append(disease)
            
            X_train = np.array(X_train)
            y_train = np.array(y_train)
            
            # Train each model
            for model_name, model in self.models.items():
                try:
                    model.fit(X_train, y_train)
                    
                    # Calculate training accuracy for reference
                    y_pred = model.predict(X_train)
                    train_accuracy = accuracy_score(y_train, y_pred)
                    
                    self.model_performance[model_name] = {
                        'train_accuracy': train_accuracy,
                        'status': 'trained'
                    }
                    print(f"✓ Trained {model_name}: {train_accuracy:.4f} accuracy")
                except Exception as e:
                    print(f"✗ Failed to train {model_name}: {str(e)}")
                    self.model_performance[model_name] = {'status': 'failed', 'error': str(e)}
        
        except Exception as e:
            print(f"Error during model training: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _create_symptom_vector(self, symptoms: List[str]) -> np.ndarray:
        """Create binary symptom vector for a disease"""
        vector = np.zeros(len(self.all_symptoms))
        for i, symptom in enumerate(self.all_symptoms):
            if any(symptom.lower() == s.lower() for s in symptoms):
                vector[i] = 1
        return vector
    
    def _create_symptom_vector_from_text(self, extracted_symptoms: List[str]) -> np.ndarray:
        """Create symptom vector from extracted symptoms"""
        vector = np.zeros(len(self.all_symptoms))
        for i, symptom in enumerate(self.all_symptoms):
            if any(symptom.lower() == s.lower() for s in extracted_symptoms):
                vector[i] = 1
        return vector
    
    def classify_symptoms(self, extracted_symptoms: List[str]) -> Dict[str, Any]:
        """
        Classify disease based on extracted symptoms using best performing model.
        Returns predictions from all models and comparison metrics.
        """
        if not extracted_symptoms:
            return {
                'success': False,
                'error': 'No symptoms provided',
                'predictions': {}
            }
        
        # Create symptom vector
        symptom_vector = self._create_symptom_vector_from_text(extracted_symptoms).reshape(1, -1)
        
        predictions = {}
        probabilities = {}
        
        # Get predictions from all models
        for model_name, model in self.models.items():
            try:
                if model_name in self.model_performance and self.model_performance[model_name].get('status') == 'failed':
                    continue
                
                pred = model.predict(symptom_vector)[0]
                predictions[model_name] = pred
                
                # Get probabilities if available
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(symptom_vector)[0]
                    disease_indices = model.classes_
                    prob_dict = {disease_indices[i]: proba[i] for i in range(len(disease_indices))}
                    probabilities[model_name] = prob_dict
            except Exception as e:
                print(f"Error predicting with {model_name}: {str(e)}")
        
        # Determine best prediction (majority voting)
        best_disease = max(set(predictions.values()), key=list(predictions.values()).count)
        confidence = list(predictions.values()).count(best_disease) / len(predictions)
        
        # Calculate evaluation metrics for this query
        query_metrics = self._calculate_query_metrics(
            extracted_symptoms=extracted_symptoms,
            predictions=predictions,
            probabilities=probabilities
        )
        
        self.last_query_metrics = query_metrics
        
        return {
            'success': True,
            'best_disease': best_disease,
            'confidence': confidence,
            'all_predictions': predictions,
            'probabilities': probabilities,
            'metrics': query_metrics,
            'symptom_vector': symptom_vector.tolist()[0],
            'extracted_symptoms': extracted_symptoms
        }
    
    def _calculate_query_metrics(self, extracted_symptoms: List[str], 
                                 predictions: Dict[str, str], 
                                 probabilities: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate evaluation metrics for a single query"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'extracted_symptoms': extracted_symptoms,
            'model_predictions': predictions,
            'confidence_scores': {},
            'kpe': self._calculate_kpe(probabilities),
            'kde': self._calculate_kde(probabilities),
            'model_agreement': self._calculate_model_agreement(predictions)
        }
        
        # Calculate confidence for each model
        for model_name, prob_dict in probabilities.items():
            if prob_dict:
                max_prob = max(prob_dict.values())
                metrics['confidence_scores'][model_name] = float(max_prob)
        
        return metrics
    
    def _calculate_kpe(self, probabilities: Dict[str, Dict]) -> Dict[str, float]:
        """Calculate Kernel Probability Entropy (KPE) for uncertainty estimation"""
        kpe_values = {}
        
        for model_name, prob_dict in probabilities.items():
            if not prob_dict:
                continue
            
            probs = np.array(list(prob_dict.values()))
            probs = probs[probs > 0]  # Remove zero probabilities
            
            if len(probs) > 0:
                # Entropy calculation
                kpe = -np.sum(probs * np.log(probs + 1e-10))
                kpe_values[model_name] = float(kpe)
        
        return kpe_values
    
    def _calculate_kde(self, probabilities: Dict[str, Dict]) -> Dict[str, float]:
        """Calculate Kernel Density Estimation (KDE) for probability distribution"""
        kde_values = {}
        
        for model_name, prob_dict in probabilities.items():
            if not prob_dict or len(prob_dict) < 2:
                continue
            
            try:
                probs = np.array(list(prob_dict.values()))
                probs = probs[probs > 0]
                
                if len(probs) > 1:
                    kde = gaussian_kde(probs)
                    kde_value = float(kde.integrate_box_1d(0, 1))
                    kde_values[model_name] = kde_value
            except Exception as e:
                print(f"KDE calculation error for {model_name}: {str(e)}")
        
        return kde_values
    
    def _calculate_model_agreement(self, predictions: Dict[str, str]) -> float:
        """Calculate agreement between models (0-1)"""
        if len(predictions) < 2:
            return 1.0
        
        pred_values = list(predictions.values())
        agreement_count = pred_values.count(max(set(pred_values), key=pred_values.count))
        return agreement_count / len(pred_values)
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get performance metrics of all trained models"""
        return self.model_performance
    
    def get_last_query_metrics(self) -> Dict[str, Any]:
        """Get metrics from the last classification query"""
        return self.last_query_metrics or {}
    
    def compare_with_rulebased(self, rule_based_result: Dict, ml_result: Dict) -> Dict[str, Any]:
        """
        Compare ML classification with rule-based classification.
        Returns comparison metrics and agreement analysis.
        """
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'rule_based_disease': rule_based_result.get('name') if isinstance(rule_based_result, dict) else rule_based_result,
            'ml_disease': ml_result['best_disease'],
            'agreement': rule_based_result.get('name') == ml_result['best_disease'] if isinstance(rule_based_result, dict) else False,
            'ml_confidence': ml_result['confidence'],
            'rule_based_match_count': rule_based_result.get('match_count', 0) if isinstance(rule_based_result, dict) else 0,
            'ml_probabilities': ml_result['probabilities'],
            'evaluation_metrics': ml_result['metrics']
        }
        
        return comparison
    
    def save_model(self, filepath: str):
        """Save trained models to disk"""
        try:
            model_data = {
                'models': self.models,
                'all_symptoms': self.all_symptoms,
                'diseases': self.diseases,
                'symptom_dict': self.symptom_dict,
                'kb_dict': self.kb_dict,
                'model_performance': self.model_performance
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"✓ Models saved to {filepath}")
            return True
        except Exception as e:
            print(f"✗ Failed to save models: {str(e)}")
            return False
    
    def load_model(self, filepath: str):
        """Load pre-trained models from disk"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.models = model_data['models']
            self.all_symptoms = model_data['all_symptoms']
            self.diseases = model_data['diseases']
            self.symptom_dict = model_data['symptom_dict']
            self.kb_dict = model_data['kb_dict']
            self.model_performance = model_data['model_performance']
            
            print(f"✓ Models loaded from {filepath}")
            return True
        except Exception as e:
            print(f"✗ Failed to load models: {str(e)}")
            return False


class MLClassifierEvaluator:
    """Evaluate ML classifier performance with confusion matrix and detailed metrics"""
    
    def __init__(self, ml_classifier: MLClassifier, disease_matcher: DiseaseMatcher = None):
        """Initialize evaluator"""
        self.ml_classifier = ml_classifier
        self.disease_matcher = disease_matcher
        self.evaluation_results = {}
    
    def evaluate(self, test_symptoms_list: List[List[str]], 
                ground_truth: List[str]) -> Dict[str, Any]:
        """
        Evaluate classifier on test data.
        
        Args:
            test_symptoms_list: List of symptom lists for test samples
            ground_truth: List of true disease labels
        
        Returns:
            Detailed evaluation metrics including confusion matrix
        """
        results = {
            'total_samples': len(ground_truth),
            'model_evaluations': {},
            'confusion_matrices': {},
            'classification_reports': {}
        }
        
        for model_name, model in self.ml_classifier.models.items():
            try:
                predictions = []
                
                for symptoms in test_symptoms_list:
                    symptom_vector = self.ml_classifier._create_symptom_vector_from_text(symptoms).reshape(1, -1)
                    pred = model.predict(symptom_vector)[0]
                    predictions.append(pred)
                
                predictions = np.array(predictions)
                ground_truth_arr = np.array(ground_truth)
                
                # Calculate metrics
                accuracy = accuracy_score(ground_truth_arr, predictions)
                precision = precision_score(ground_truth_arr, predictions, average='weighted', zero_division=0)
                recall = recall_score(ground_truth_arr, predictions, average='weighted', zero_division=0)
                f1 = f1_score(ground_truth_arr, predictions, average='weighted', zero_division=0)
                
                # Confusion matrix
                cm = confusion_matrix(ground_truth_arr, predictions)
                
                # Classification report
                class_report = classification_report(
                    ground_truth_arr, 
                    predictions, 
                    output_dict=True,
                    zero_division=0
                )
                
                results['model_evaluations'][model_name] = {
                    'accuracy': float(accuracy),
                    'precision': float(precision),
                    'recall': float(recall),
                    'f1_score': float(f1)
                }
                
                results['confusion_matrices'][model_name] = cm.tolist()
                results['classification_reports'][model_name] = class_report
                
            except Exception as e:
                print(f"Error evaluating {model_name}: {str(e)}")
        
        self.evaluation_results = results
        return results
    
    def get_evaluation_summary(self) -> Dict[str, Any]:
        """Get summary of evaluation results"""
        if not self.evaluation_results:
            return {'error': 'No evaluation results available'}
        
        summary = {
            'total_samples': self.evaluation_results['total_samples'],
            'best_model': None,
            'best_accuracy': 0,
            'all_accuracies': {},
            'model_rankings': []
        }
        
        # Find best model
        for model_name, metrics in self.evaluation_results['model_evaluations'].items():
            accuracy = metrics['accuracy']
            summary['all_accuracies'][model_name] = accuracy
            
            if accuracy > summary['best_accuracy']:
                summary['best_accuracy'] = accuracy
                summary['best_model'] = model_name
        
        # Rank models
        summary['model_rankings'] = sorted(
            summary['all_accuracies'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return summary
