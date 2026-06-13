#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medicine Availability Service
Handles medicine search and availability checks in pharmacies.
"""

import csv
import math
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class MedicineService:
    """Service for managing medicine availability and pharmacy searches."""

    def __init__(self, medicines_csv: str = None):
        """
        Initialize the medicine service.
        
        Args:
            medicines_csv: Path to CSV file with medicine data
        """
        self.medicines_data = []
        self.pharmacies_data = []
        self.medicine_index = {}
        
        if medicines_csv:
            self.load_medicines_data(medicines_csv)

    def load_medicines_data(self, csv_path: str):
        """Load medicines from CSV file."""
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.medicines_data = list(reader)
                # Create index for faster lookups
                for item in self.medicines_data:
                    medicine_name = item.get('medicine_name', '').lower()
                    if medicine_name:
                        self.medicine_index[medicine_name] = item
        except Exception as e:
            print(f"Error loading medicines data: {e}")

    def search_medicine(self, medicine_name: str) -> Optional[Dict]:
        """
        Search for a medicine by name.
        
        Args:
            medicine_name: Name of the medicine to search
            
        Returns:
            Dictionary with medicine details or None if not found
        """
        medicine_name_lower = medicine_name.lower().strip()
        
        # Direct lookup
        if medicine_name_lower in self.medicine_index:
            return self.medicine_index[medicine_name_lower]
        
        # Partial match
        for name, data in self.medicine_index.items():
            if name in medicine_name_lower or medicine_name_lower in name:
                return data
        
        return None

    def find_nearby_pharmacies(
        self, 
        latitude: float, 
        longitude: float, 
        radius_km: float = 5.0
    ) -> List[Dict]:
        """
        Find pharmacies near a given location.
        
        Args:
            latitude: User's latitude
            longitude: User's longitude
            radius_km: Search radius in kilometers
            
        Returns:
            List of nearby pharmacies
        """
        nearby = []
        
        for pharmacy in self.pharmacies_data:
            try:
                pharm_lat = float(pharmacy.get('latitude', 0))
                pharm_lon = float(pharmacy.get('longitude', 0))
                
                # Calculate distance using Haversine formula
                distance = self._calculate_distance(
                    latitude, longitude, pharm_lat, pharm_lon
                )
                
                if distance <= radius_km:
                    pharmacy_copy = pharmacy.copy()
                    pharmacy_copy['distance_km'] = round(distance, 2)
                    nearby.append(pharmacy_copy)
            except (ValueError, KeyError):
                continue
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance_km'])
        return nearby

    def check_medicine_availability(
        self,
        medicine_name: str,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0
    ) -> Dict:
        """
        Check availability of a medicine in nearby pharmacies.
        
        Args:
            medicine_name: Name of the medicine
            latitude: User's latitude
            longitude: User's longitude
            radius_km: Search radius in kilometers
            
        Returns:
            Dictionary with availability information
        """
        medicine = self.search_medicine(medicine_name)
        
        if not medicine:
            return {
                'success': False,
                'message': f'Medicine "{medicine_name}" not found in database',
                'available': False
            }
        
        nearby_pharmacies = self.find_nearby_pharmacies(
            latitude, longitude, radius_km
        )
        
        if not nearby_pharmacies:
            return {
                'success': True,
                'medicine_name': medicine_name,
                'available': False,
                'message': f'No pharmacies found within {radius_km} km',
                'nearest_pharmacy': None
            }
        
        return {
            'success': True,
            'medicine_name': medicine_name,
            'medicine_details': medicine,
            'available': True,
            'nearby_pharmacies': nearby_pharmacies[:5],  # Top 5 nearest
            'nearest_pharmacy': nearby_pharmacies[0] if nearby_pharmacies else None
        }

    @staticmethod
    def _calculate_distance(
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        
        Args:
            lat1, lon1: First coordinate (decimal degrees)
            lat2, lon2: Second coordinate (decimal degrees)
            
        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c

    def get_statistics(self) -> Dict:
        """Get statistics about medicines and pharmacies."""
        return {
            'total_medicines': len(self.medicines_data),
            'total_pharmacies': len(self.pharmacies_data),
            'medicine_categories': len(set(m.get('category', '') for m in self.medicines_data))
        }


# Singleton instance
_service = None


def get_medicine_service(medicines_csv: str = None) -> MedicineService:
    """Get or create the medicine service singleton."""
    global _service
    if _service is None:
        _service = MedicineService(medicines_csv)
    return _service
