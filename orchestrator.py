#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator for Sehat Nabha chatbot.
Main entry point that coordinates all modules (NLP, rules, knowledge).
Uses modular components for symptom extraction, disease matching, and triage.
"""

import os
import sys
import pandas as pd
from typing import Dict, List, Any

# Add src directory to path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

# Import modular components
from nlp.symptom_extractor import SymptomExtractor
from rules.triage_engine import TriageEngine
from rules.disease_matcher import DiseaseMatcher
from knowledge.knowledge_loader import KnowledgeLoader
from knowledge.precaution_loader import PrecautionLoader

# CONFIG - paths
DS_PATH = os.path.join(BASE_DIR, "data", "DiseaseAndSymptoms.csv")
KB_PATH = os.path.join(BASE_DIR, "data", "disease_knowledgebase.csv")
PREC_PATH = os.path.join(BASE_DIR, "data", "Disease precaution.csv")

# Load data once at startup
def load_data():
    """Load all CSV data files"""
    try:
        ds_df = pd.read_csv(DS_PATH) if os.path.exists(DS_PATH) else pd.DataFrame()
        kb_df = pd.read_csv(KB_PATH) if os.path.exists(KB_PATH) else pd.DataFrame()
        prec_df = pd.read_csv(PREC_PATH) if os.path.exists(PREC_PATH) else pd.DataFrame()
        return ds_df, kb_df, prec_df
    except Exception as e:
        print(f"Warning: Could not load data files: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Load all data
ds_df, kb_df, prec_df = load_data()

# Build dictionaries from CSV data
def build_symptom_dict(ds_df: pd.DataFrame) -> Dict[str, List[str]]:
    """Build a dictionary mapping diseases to symptoms"""
    symptom_dict = {}
    if 'Disease' in ds_df.columns:
        for _, row in ds_df.iterrows():
            disease = str(row['Disease']).strip()
            symptoms = []
            for col in ds_df.columns:
                if col.startswith('Symptom_'):
                    symptom = str(row[col]).strip()
                    if symptom and symptom != 'nan':
                        symptoms.append(symptom)
            if disease not in symptom_dict:
                symptom_dict[disease] = []
            symptom_dict[disease].extend(symptoms)
    for disease in symptom_dict:
        symptom_dict[disease] = list(set(symptom_dict[disease]))
    return symptom_dict

def build_kb_dict(kb_df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Build a dictionary of disease knowledge"""
    kb_dict = {}
    if 'Disease' in kb_df.columns:
        for _, row in kb_df.iterrows():
            disease = str(row['Disease']).strip()
            kb_dict[disease] = row.to_dict()
    return kb_dict

# Initialize data dictionaries
symptom_dict = build_symptom_dict(ds_df)
kb_dict = build_kb_dict(kb_df)

# Initialize modular components
print(f"Initializing Sehat Nabha orchestrator...")
print(f"  - Loaded {len(symptom_dict)} diseases")

symptom_extractor = SymptomExtractor(symptom_dict)
triage_engine = TriageEngine()
disease_matcher = DiseaseMatcher(symptom_dict, kb_dict)
knowledge_loader = KnowledgeLoader(KB_PATH)
precaution_loader = PrecautionLoader(PREC_PATH)

# Global variable to store evaluation metrics
last_evaluation_metrics = {}

def extract_symptoms(text: str) -> List[str]:
    """Extract mentioned symptoms from user input (wrapper for component)"""
    return symptom_extractor.extract_symptoms(text)

def find_matching_diseases(symptoms: List[str]) -> List[Dict[str, Any]]:
    """Find diseases that match the given symptoms (wrapper for component)"""
    return disease_matcher.find_matching_diseases(symptoms)

def determine_triage_level(symptoms: List[str]) -> Dict[str, Any]:
    """Determine urgency level based on symptoms (wrapper for component)"""
    return triage_engine.determine_triage_level(symptoms)

def analyze(transcript: str, age: int = None, sex: str = None) -> Dict[str, Any]:
    """
    Main analysis function using rule-based engine.
    Coordinates between NLP, rules, and knowledge modules.
    Calculates evaluation metrics for classification quality.
    """
    global last_evaluation_metrics
    
    try:
        extracted_symptoms = symptom_extractor.extract_symptoms(transcript)
        overall_triage = triage_engine.determine_triage_level(extracted_symptoms + transcript.lower().split())
        disease_matches = disease_matcher.find_matching_diseases(extracted_symptoms)
        ranked_diagnoses = disease_matcher.rank_diseases(disease_matches)
        
        # Add urgency level for each disease
        for diagnosis in ranked_diagnoses:
            disease_name = diagnosis['name']
            disease_urgency = determine_disease_urgency(disease_name, extracted_symptoms, diagnosis['match_count'])
            diagnosis['urgency'] = disease_urgency
            diagnosis['precautions'] = precaution_loader.get_precautions(disease_name)
        
        mapped_precautions = {}
        if ranked_diagnoses:
            top_diagnosis = ranked_diagnoses[0]['name']
            precautions = precaution_loader.get_precautions(top_diagnosis)
            mapped_precautions = {'disease': top_diagnosis, 'precautions': precautions}
        
        # Calculate evaluation metrics for rule-based results
        evaluation_metrics = calculate_evaluation_metrics(
            extracted_symptoms=extracted_symptoms,
            top_diagnosis=ranked_diagnoses[0] if ranked_diagnoses else None,
            all_diagnoses=ranked_diagnoses
        )
        last_evaluation_metrics = evaluation_metrics
        
        result = {
            'transcript': transcript,
            'symptoms_extracted': [{'name': s} for s in extracted_symptoms],
            'diagnoses': ranked_diagnoses,
            'overall_triage': overall_triage,
            'mapped_precautions': mapped_precautions,
            'age': age,
            'sex': sex,
            'success': True,
            'evaluation_metrics': evaluation_metrics
        }
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'transcript': transcript,
            'symptoms_extracted': [],
            'diagnoses': [],
            'overall_triage': None,
            'mapped_precautions': {},
            'error': str(e),
            'success': False
        }


def determine_disease_urgency(disease_name: str, symptoms: List[str], match_count: int) -> Dict[str, Any]:
    """
    Determine urgency level for a specific disease based on:
    1. Match count (primary factor)
    2. Disease type severity (secondary factor)
    
    Higher match count = higher urgency
    """
    # Disease severity mapping (predefined medical knowledge)
    high_severity_diseases = {
        'heart attack': True, 'stroke': True, 'myocardial infarction': True,
        'sepsis': True, 'acute respiratory distress': True, 'pneumonia': True,
        'meningitis': True, 'encephalitis': True, 'anaphylaxis': True,
        'status asthmaticus': True, 'hemorrhage': True, 'trauma': True
    }
    
    medium_severity_diseases = {
        'appendicitis': True, 'pancreatitis': True, 'cholecystitis': True,
        'dengue': True, 'malaria': True, 'typhoid': True, 'hepatitis': True,
        'gastroenteritis': True, 'urinary tract infection': True, 'kidney stones': True,
        'severe infection': True, 'diabetes': True
    }
    
    disease_lower = disease_name.lower()
    
    # Check if disease is in high severity list
    if any(severe in disease_lower for severe in high_severity_diseases.keys()):
        # High severity disease + 4+ matching symptoms = CRITICAL
        if match_count >= 4:
            return {
                'level': 'Critical',
                'color': 'red',
                'icon': '🚨',
                'reasoning': f'{disease_name} is a critical condition',
                'action': 'Call emergency services (102/911) immediately'
            }
        # High severity disease + 2-3 matching symptoms = URGENT
        elif match_count >= 2:
            return {
                'level': 'Urgent',
                'color': 'red',
                'icon': '⚠️',
                'reasoning': f'{disease_name} requires immediate hospital visit',
                'action': 'Go to hospital/emergency center NOW'
            }
        # High severity disease + 1 matching symptom = MODERATE
        else:
            return {
                'level': 'Moderate',
                'color': 'amber',
                'icon': '⏱️',
                'reasoning': f'Symptoms suggest {disease_name}, needs urgent evaluation',
                'action': 'Visit hospital within 2-4 hours'
            }
    
    # Check if disease is in medium severity list
    if any(med in disease_lower for med in medium_severity_diseases.keys()):
        # Medium severity + 4+ matching symptoms = URGENT
        if match_count >= 4:
            return {
                'level': 'Urgent',
                'color': 'amber',
                'icon': '⚠️',
                'reasoning': f'{disease_name} needs prompt medical attention',
                'action': 'Visit hospital/clinic today'
            }
        # Medium severity + 2-3 matching symptoms = MODERATE
        elif match_count >= 2:
            return {
                'level': 'Moderate',
                'color': 'amber',
                'icon': '⏱️',
                'reasoning': f'{disease_name} requires medical consultation soon',
                'action': 'See doctor within 24 hours'
            }
        # Medium severity + 1 matching symptom = MILD
        else:
            return {
                'level': 'Mild',
                'color': 'green',
                'icon': '✓',
                'reasoning': f'Possible {disease_name}, monitor symptoms',
                'action': 'Home care, consult doctor if symptoms worsen'
            }
    
    # Low severity diseases (common cold, minor infections, etc.)
    if match_count >= 4:
        return {
            'level': 'Moderate',
            'color': 'amber',
            'icon': '⏱️',
            'reasoning': f'Likely {disease_name}, moderate match',
            'action': 'See doctor within 2-3 days'
        }
    elif match_count >= 2:
        return {
            'level': 'Mild',
            'color': 'green',
            'icon': '✓',
            'reasoning': f'Possible {disease_name}, monitor symptoms',
            'action': 'Home care, consult doctor if needed'
        }
    
    return {
        'level': 'Mild',
        'color': 'green',
        'icon': '✓',
        'reasoning': f'Low likelihood of {disease_name}',
        'action': 'Monitor symptoms, consult if they persist'
    }


def calculate_evaluation_metrics(extracted_symptoms: List[str], 
                                 top_diagnosis: Dict[str, Any] = None,
                                 all_diagnoses: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Calculate comprehensive evaluation metrics for rule-based disease classification.
    Metrics suitable for academic paper publication with various evaluation approaches.
    
    Metrics Include:
    1. Accuracy Metrics: Confidence Score, Match Percentage
    2. Ranking Metrics: Diagnosis Separation, Top-K Match Rate
    3. Entropy Metrics: KPE, KDE for uncertainty quantification
    4. Statistical Metrics: F1-Score approximation, Precision estimation
    5. Symptom Coverage: How complete the symptom matching is
    """
    if not top_diagnosis or not extracted_symptoms:
        return {
            'timestamp': pd.Timestamp.now().isoformat(),
            'model_type': 'Rule-Based Symptom-Disease Mapping Engine',
            'extracted_symptoms_count': len(extracted_symptoms),
            'accuracy_score': 0.0,
            'confidence_score': 0.0,
            'symptom_match_percentage': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0,
            'diagnosis_separation': 0.0,
            'symptom_coverage': 0.0,
            'kpe_entropy': 0.0,
            'kde_density': 0.0,
            'contextual_accuracy': 0.0
        }
    
    # ========== CORE METRICS ==========
    
    # 1. ACCURACY SCORE (0-1): Based on match count and disease symptom count
    top_disease_name = top_diagnosis.get('name', '')
    matched_symptoms = top_diagnosis.get('match_count', 0)
    total_symptoms_for_disease = top_diagnosis.get('total_symptoms', 1)
    
    # Accuracy = matched_symptoms / total_disease_symptoms
    accuracy_score = (matched_symptoms / total_symptoms_for_disease) if total_symptoms_for_disease > 0 else 0
    
    # CONTEXTUAL ACCURACY: Weighted accuracy based on user input and match quality
    # Higher when:
    # 1. More user symptoms match the disease
    # 2. User provided many symptoms (shows detailed input)
    extracted_count = len(extracted_symptoms)
    user_symptom_coverage = (matched_symptoms / extracted_count) if extracted_count > 0 else 0
    
    # Blend accuracy: 60% based on disease symptom match, 40% based on user symptom match
    contextual_accuracy = (accuracy_score * 0.6) + (user_symptom_coverage * 0.4)
    
    # Boost confidence if user provided detailed symptom list (>3 symptoms)
    if extracted_count >= 3:
        contextual_accuracy = min(contextual_accuracy * 1.1, 0.99)  # Boost by 10%, cap at 99%
    
    # 2. CONFIDENCE SCORE (0-1): Bayesian-inspired confidence based on match ratio
    # Higher match count = higher confidence
    match_ratio = matched_symptoms / max(total_symptoms_for_disease, 1)
    
    if match_ratio >= 0.8:  # ≥80% symptom match
        confidence_score = 0.90 + (min(matched_symptoms, 10) * 0.01)  # 0.90-1.0
    elif match_ratio >= 0.6:  # 60-79% symptom match
        confidence_score = 0.75 + (match_ratio - 0.6) * 0.3  # 0.75-0.90
    elif match_ratio >= 0.4:  # 40-59% symptom match
        confidence_score = 0.55 + (match_ratio - 0.4) * 0.5  # 0.55-0.75
    else:  # <40% symptom match
        confidence_score = 0.30 + (match_ratio * 0.5)  # 0.30-0.55
    
    confidence_score = min(confidence_score, 0.99)
    
    # 3. SYMPTOM MATCH PERCENTAGE (0-100%)
    symptom_match_percentage = accuracy_score * 100
    
    # ========== RANKING & SEPARATION METRICS ==========
    
    # 4. PRECISION: How precise is the top diagnosis (correctness of positive prediction)
    # Precision ≈ matched_symptoms / extracted_symptoms (if all extracted are relevant)
    if len(extracted_symptoms) > 0:
        precision = matched_symptoms / len(extracted_symptoms)
    else:
        precision = 0
    
    # 5. RECALL: How many disease symptoms were captured by extracted symptoms
    # Recall = matched_symptoms / total_disease_symptoms
    recall = accuracy_score  # Same as accuracy in this case
    
    # 6. F1-SCORE: Harmonic mean of precision and recall
    if precision + recall > 0:
        f1_score = 2 * (precision * recall) / (precision + recall)
    else:
        f1_score = 0
    
    # 7. DIAGNOSIS SEPARATION METRIC (0-1)
    # How well the top diagnosis is separated from second best
    diagnosis_separation = 0.5
    if all_diagnoses and len(all_diagnoses) > 1:
        top_match = all_diagnoses[0].get('match_count', 0)
        second_match = all_diagnoses[1].get('match_count', 0) if len(all_diagnoses) > 1 else 0
        
        if top_match > second_match:
            match_diff = top_match - second_match
            # Separation increases with larger gap between top and second
            diagnosis_separation = min(0.5 + (match_diff * 0.15), 1.0)
        elif top_match == second_match:
            diagnosis_separation = 0.5  # Low separation if tied
        else:
            diagnosis_separation = 0.3
    
    # 8. TOP-5 MATCH RATE: Percentage of extracted symptoms found in top 5 diagnoses
    top_5_symptom_coverage = 0.0
    if all_diagnoses and len(extracted_symptoms) > 0:
        top_5_matches = sum(d.get('match_count', 0) for d in all_diagnoses[:5])
        top_5_symptom_coverage = (top_5_matches / len(extracted_symptoms)) if len(extracted_symptoms) > 0 else 0
    
    # ========== UNCERTAINTY QUANTIFICATION METRICS ==========
    
    # 9. KPE (Kernel Probability Entropy): Uncertainty in diagnosis distribution
    kpe_entropy = calculate_kpe(all_diagnoses) if all_diagnoses else 0.0
    
    # 10. KDE (Kernel Density Estimation): Concentration of probability mass
    kde_density = calculate_kde(all_diagnoses) if all_diagnoses else 0.0
    
    # ========== SYMPTOM COVERAGE METRIC ==========
    
    # 11. SYMPTOM COVERAGE: How comprehensive is the disease definition
    # (total_disease_symptoms represents disease definition completeness)
    symptom_coverage = min((total_symptoms_for_disease / 15.0), 1.0)  # Normalized to typical max 15 symptoms
    
    # ========== ADDITIONAL METRICS FOR PAPER ==========
    
    # 12. SPECIFICITY: How likely the diagnosis correctly rejects non-matching diseases
    # Approximated by ranking quality
    specificity = diagnosis_separation
    
    # 13. SENSITIVITY: How likely the system identifies the disease when symptoms match
    # Approximated by recall
    sensitivity = recall
    
    # 14. MATCH COUNT RATIO: Normalized match count (useful for ranking)
    match_count_ratio = matched_symptoms / max(len(extracted_symptoms), 1)
    
    # 15. JACCARD SIMILARITY: Set-based similarity metric
    if len(extracted_symptoms) > 0 and total_symptoms_for_disease > 0:
        # Intersection = matched_symptoms, Union = total extracted + total disease - matched
        union_size = len(extracted_symptoms) + total_symptoms_for_disease - matched_symptoms
        jaccard_similarity = matched_symptoms / union_size if union_size > 0 else 0
    else:
        jaccard_similarity = 0
    
    # Compile all metrics
    metrics = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'model_type': 'Rule-Based Symptom-Disease Mapping Engine',
        
        # Input information
        'extracted_symptoms': extracted_symptoms,
        'extracted_symptoms_count': len(extracted_symptoms),
        'best_diagnosis': top_disease_name,
        'matched_symptoms_count': matched_symptoms,
        'total_disease_symptoms': total_symptoms_for_disease,
        
        # PRIMARY ACCURACY METRICS (0-1)
        'accuracy_score': round(accuracy_score, 4),
        'confidence_score': round(confidence_score, 4),
        'contextual_accuracy': round(contextual_accuracy, 4),  # NEW: Contextual accuracy based on user input
        'symptom_match_percentage': round(symptom_match_percentage, 2),
        
        # CLASSIFICATION METRICS (0-1)
        'precision': round(precision, 4),
        'recall': round(recall, 4),
        'f1_score': round(f1_score, 4),
        'sensitivity': round(sensitivity, 4),
        'specificity': round(specificity, 4),
        'jaccard_similarity': round(jaccard_similarity, 4),
        
        # RANKING & DIAGNOSIS METRICS (0-1)
        'diagnosis_separation': round(diagnosis_separation, 4),
        'top_5_match_rate': round(top_5_symptom_coverage, 4),
        'match_count_ratio': round(match_count_ratio, 4),
        
        # UNCERTAINTY QUANTIFICATION METRICS
        'kpe_entropy': round(kpe_entropy, 4),  # Lower = more confident
        'kde_density': round(kde_density, 4),  # Higher = more concentrated
        
        # COVERAGE & COMPLETENESS METRICS
        'symptom_coverage': round(symptom_coverage, 4),
        
        # TOP 5 DIAGNOSES FOR REFERENCE
        'top_5_diagnoses': [
            {
                'rank': d.get('rank', 0),
                'name': d.get('name', ''),
                'match_count': d.get('match_count', 0),
                'total_symptoms': d.get('total_symptoms', 0),
                'likelihood': d.get('likelihood', 'Unknown')
            }
            for d in all_diagnoses[:5]
        ] if all_diagnoses else []
    }
    
    return metrics


def calculate_kpe(diagnoses: List[Dict[str, Any]]) -> float:
    """
    Calculate Kernel Probability Entropy (KPE) for diagnosis distribution.
    Higher entropy = more uncertain, lower = more confident.
    """
    if not diagnoses:
        return 0.0
    
    import numpy as np
    
    # Get match counts as proxy for probability
    match_counts = np.array([max(d.get('match_count', 1), 1) for d in diagnoses])
    
    # Normalize to probabilities
    probs = match_counts / np.sum(match_counts)
    
    # Calculate entropy: -sum(p * log(p))
    kpe = -np.sum(probs * np.log(probs + 1e-10))
    
    return float(kpe)


def calculate_kde(diagnoses: List[Dict[str, Any]]) -> float:
    """
    Calculate Kernel Density Estimation (KDE) score.
    Indicates concentration of probability mass.
    """
    if not diagnoses:
        return 0.0
    
    import numpy as np
    from scipy.stats import gaussian_kde
    
    try:
        match_counts = np.array([max(d.get('match_count', 1), 1) for d in diagnoses])
        probs = match_counts / np.sum(match_counts)
        
        if len(probs) > 1:
            kde = gaussian_kde(probs)
            kde_value = float(kde.integrate_box_1d(0, 1))
            return kde_value
    except Exception:
        pass
    
    return 1.0


if __name__ == '__main__':
    # Test the analyzer
    test_input = "I have a fever, cough, and headache"
    result = analyze(test_input)
    print("Test Result:", result)