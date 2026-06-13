# -*- coding: utf-8 -*-
"""
Disease Matcher
Finds diseases that match extracted symptoms.
"""

from typing import Dict, List, Any


class DiseaseMatcher:
    """Match symptoms to diseases"""
    
    def __init__(self, symptom_dict: Dict[str, List[str]] = None, kb_dict: Dict[str, Any] = None):
        """
        Initialize matcher with symptom and knowledge base dictionaries.
        
        symptom_dict: mapping of disease -> list of symptoms
        kb_dict: mapping of disease -> disease information
        """
        self.symptom_dict = symptom_dict or {}
        self.kb_dict = kb_dict or {}
    
    def find_matching_diseases(self, symptoms: List[str], max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Find diseases that match the given symptoms.
        Only returns diseases where ALL extracted symptoms are present.
        
        Args:
            symptoms: List of symptom names
            max_results: Maximum number of results to return
        
        Returns:
            List of matching diseases with match count
        """
        disease_scores = {}
        
        # If no symptoms provided, return empty list
        if not symptoms:
            return []
        
        for disease, disease_symptoms in self.symptom_dict.items():
            # Count how many user symptoms match this disease
            matches = sum(
                1 for s in symptoms 
                if any(s.lower() in ds.lower() for ds in disease_symptoms)
            )
            
            # Only include disease if ALL extracted symptoms are present
            if matches == len(symptoms):
                disease_scores[disease] = {
                    'name': disease,
                    'match_count': matches,
                    'total_symptoms': len(disease_symptoms),
                    'knowledge': self.kb_dict.get(disease, {}),
                }
        
        # Sort by match count (number of matching symptoms) and return all matches
        sorted_diseases = sorted(
            disease_scores.items(),
            key=lambda x: x[1]['match_count'],
            reverse=True
        )
        
        return [disease[1] for disease in sorted_diseases[:max_results]]
    
    def get_disease_likelihood(self, score: float) -> str:
        """Convert score to likelihood string"""
        if score >= 70:
            return 'High'
        elif score >= 40:
            return 'Medium'
        else:
            return 'Low'
    
    def rank_diseases(self, diseases: List[Dict]) -> List[Dict]:
        """
        Rank diseases by match count and add likelihood assessment.
        Does NOT include match_score - only shows match count.
        """
        ranked = []
        for i, disease in enumerate(diseases, 1):
            ranked.append({
                'rank': i,
                'name': disease['name'],
                'match_count': disease['match_count'],
                'total_symptoms': disease['total_symptoms'],
                'likelihood': self.get_disease_likelihood_from_count(disease['match_count']),
                'reasoning': f"Matched {disease['match_count']} symptom(s)"
            })
        return ranked
    
    def get_disease_likelihood_from_count(self, match_count: int) -> str:
        """Convert match count to likelihood string"""
        if match_count >= 4:
            return 'High'
        elif match_count >= 2:
            return 'Medium'
        else:
            return 'Low'
