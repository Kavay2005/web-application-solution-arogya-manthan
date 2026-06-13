# -*- coding: utf-8 -*-
"""
Symptom Extractor
Extracts and matches symptoms from user input.
"""

from typing import Dict, List


class SymptomExtractor:
    """Extract symptoms from text and match against known symptoms"""
    
    def __init__(self, symptom_dict: Dict[str, List[str]] = None):
        """
        Initialize with a symptom dictionary.
        symptom_dict: mapping of disease -> list of symptoms
        """
        self.symptom_dict = symptom_dict or {}
    
    def extract_symptoms(self, text: str) -> List[str]:
        """
        Extract ONLY the exact symptoms mentioned by the user from the text.
        Matches user input directly against known symptoms in the database.
        Returns only symptoms that are actually mentioned.
        """
        import re
        
        text_lower = text.lower()
        mentioned_symptoms = []
        seen_symptoms_lower = set()
        
        # Collect all unique symptoms from symptom_dict
        all_symptoms = {}
        for disease, symptoms in self.symptom_dict.items():
            for symptom in symptoms:
                symptom_lower = symptom.lower()
                if symptom_lower not in all_symptoms:
                    all_symptoms[symptom_lower] = symptom
        
        # Create a list sorted by length (longest first) to match compound symptoms first
        sorted_symptoms = sorted(all_symptoms.items(), key=lambda x: len(x[0]), reverse=True)
        
        # Extract clean words from text (remove punctuation)
        text_words = re.findall(r'\b\w+\b', text_lower)
        text_phrase = ' ' + ' '.join(text_words) + ' '
        
        # Check each symptom for exact presence in text
        for symptom_lower, symptom_original in sorted_symptoms:
            if symptom_lower in seen_symptoms_lower:
                continue
            
            # Replace underscores with spaces for matching
            symptom_for_matching = symptom_lower.replace('_', ' ')
            
            # Check if symptom phrase appears in text with word boundaries
            symptom_phrase = ' ' + symptom_for_matching + ' '
            
            if symptom_phrase in text_phrase:
                # Exact match found
                mentioned_symptoms.append(symptom_original)
                seen_symptoms_lower.add(symptom_lower)
            else:
                # Check if it's a single-word symptom
                if '_' not in symptom_lower:
                    # Single word symptom - check if it exists as a whole word in text
                    if ' ' + symptom_lower + ' ' in text_phrase or \
                       text_lower.startswith(symptom_lower + ' ') or \
                       text_lower.endswith(' ' + symptom_lower) or \
                       text_lower == symptom_lower:
                        mentioned_symptoms.append(symptom_original)
                        seen_symptoms_lower.add(symptom_lower)
        
        return mentioned_symptoms
    
    def get_all_symptoms(self) -> List[str]:
        """Get list of all known symptoms"""
        all_symptoms = set()
        for symptoms in self.symptom_dict.values():
            all_symptoms.update(symptoms)
        return sorted(list(all_symptoms))
    
    def symptom_to_diseases(self, symptom: str) -> List[str]:
        """Find all diseases that have this symptom"""
        symptom_lower = symptom.lower()
        diseases = []
        
        for disease, symptoms in self.symptom_dict.items():
            for s in symptoms:
                if s.lower() == symptom_lower:
                    diseases.append(disease)
                    break
        
        return diseases
