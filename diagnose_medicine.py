#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medicine Diagnosis Module
Connects disease diagnosis with recommended medicines.
"""

import json
import os
from typing import Dict, List, Optional
from src.medicine.medicine_service import get_medicine_service


class MedicineDiagnoser:
    """Handles medicine recommendations based on diagnosis."""

    def __init__(self):
        """Initialize the medicine diagnoser."""
        self.medicine_service = get_medicine_service()
        self.disease_medicine_map = self._load_disease_medicine_map()

    def _load_disease_medicine_map(self) -> Dict[str, List[str]]:
        """Load the mapping of diseases to recommended medicines."""
        disease_medicine_file = 'data/disease_medicine_mapping.json'
        
        if os.path.exists(disease_medicine_file):
            try:
                with open(disease_medicine_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading disease-medicine mapping: {e}")
        
        # Default mapping
        return {
            'fever': ['aspirin', 'paracetamol', 'ibuprofen'],
            'cold': ['cough syrup', 'vitamin c', 'throat lozenges'],
            'cough': ['cough syrup', 'throat lozenges', 'honey'],
            'headache': ['aspirin', 'ibuprofen', 'paracetamol'],
            'stomach_pain': ['antacid', 'omeprazole', 'loperamide'],
            'diarrhea': ['loperamide', 'oral rehydration salts'],
            'allergy': ['antihistamine', 'cetirizine', 'loratadine'],
            'asthma': ['salbutamol', 'inhaler'],
            'hypertension': ['amlodipine', 'lisinopril'],
            'diabetes': ['metformin', 'insulin'],
        }

    def diagnose_and_recommend_medicines(
        self,
        disease: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: float = 5.0
    ) -> Dict:
        """
        Get medicine recommendations for a disease and check availability.
        
        Args:
            disease: Disease name
            latitude: User's latitude (optional)
            longitude: User's longitude (optional)
            radius_km: Search radius in kilometers
            
        Returns:
            Dictionary with medicine recommendations and availability
        """
        disease_lower = disease.lower().strip()
        
        # Get recommended medicines for this disease
        recommended_medicines = self.disease_medicine_map.get(
            disease_lower, 
            []
        )
        
        if not recommended_medicines:
            return {
                'success': False,
                'error': f'No medicine recommendations found for "{disease}"',
                'recommendations': []
            }
        
        recommendations = []
        
        for medicine_name in recommended_medicines:
            medicine_result = {
                'medicine_name': medicine_name,
                'available': False,
                'nearby_pharmacies': []
            }
            
            # Check availability if location provided
            if latitude is not None and longitude is not None:
                availability = self.medicine_service.check_medicine_availability(
                    medicine_name,
                    latitude,
                    longitude,
                    radius_km
                )
                
                if availability.get('success'):
                    medicine_result['available'] = availability.get('available', False)
                    medicine_result['nearby_pharmacies'] = availability.get(
                        'nearby_pharmacies', []
                    )[:3]  # Top 3 pharmacies
            
            recommendations.append(medicine_result)
        
        return {
            'success': True,
            'disease': disease,
            'recommendations': recommendations,
            'total_medicines': len(recommendations)
        }

    def get_alternative_medicines(self, medicine_name: str) -> List[str]:
        """Get alternative medicines for a given medicine."""
        medicine_lower = medicine_name.lower().strip()
        
        # Find which diseases this medicine is used for
        related_diseases = []
        for disease, medicines in self.disease_medicine_map.items():
            if any(med.lower() in medicine_lower or medicine_lower in med.lower() 
                   for med in medicines):
                related_diseases.append(disease)
        
        # Collect alternatives from related diseases
        alternatives = set()
        for disease in related_diseases:
            alternatives.update(self.disease_medicine_map.get(disease, []))
        
        # Remove the original medicine
        alternatives.discard(medicine_name)
        
        return list(alternatives)


# Global instance
_diagnoser = None


def get_medicine_diagnoser() -> MedicineDiagnoser:
    """Get or create the medicine diagnoser singleton."""
    global _diagnoser
    if _diagnoser is None:
        _diagnoser = MedicineDiagnoser()
    return _diagnoser


if __name__ == '__main__':
    # Test the module
    diagnoser = get_medicine_diagnoser()
    
    # Example: Get medicine recommendations for fever
    result = diagnoser.diagnose_and_recommend_medicines('fever')
    print(json.dumps(result, indent=2))
    
    # Get alternatives for aspirin
    alternatives = diagnoser.get_alternative_medicines('aspirin')
    print(f"Alternatives for aspirin: {alternatives}")
