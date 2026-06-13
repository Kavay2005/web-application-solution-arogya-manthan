#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medicine Response Testing Module
Tests medicine availability and recommendation APIs.
"""

import requests
import json
from typing import Dict, List


class MedicineResponseTester:
    """Tests medicine API responses."""

    def __init__(self, api_base_url: str = 'http://localhost:5000/api'):
        """
        Initialize the tester.
        
        Args:
            api_base_url: Base URL for the API
        """
        self.api_base_url = api_base_url
        self.test_results = []

    def test_medicine_search(self, medicine_name: str) -> Dict:
        """
        Test medicine search API.
        
        Args:
            medicine_name: Name of medicine to search
            
        Returns:
            Test result dictionary
        """
        try:
            url = f"{self.api_base_url}/medicine-search"
            payload = {
                "medicine": medicine_name,
                "lat": 33.68,  # Sample latitude (Islamabad)
                "lon": 73.04   # Sample longitude
            }
            
            response = requests.get(url, params=payload, timeout=10)
            
            return {
                'test': 'medicine_search',
                'medicine': medicine_name,
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else str(response.text)
            }
        except Exception as e:
            return {
                'test': 'medicine_search',
                'medicine': medicine_name,
                'success': False,
                'error': str(e)
            }

    def test_pharmacy_nearby(self, latitude: float, longitude: float) -> Dict:
        """
        Test finding nearby pharmacies.
        
        Args:
            latitude: User's latitude
            longitude: User's longitude
            
        Returns:
            Test result dictionary
        """
        try:
            url = f"{self.api_base_url}/pharmacy-nearby"
            payload = {
                "lat": latitude,
                "lon": longitude,
                "radius": 5
            }
            
            response = requests.get(url, params=payload, timeout=10)
            
            return {
                'test': 'pharmacy_nearby',
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else str(response.text)
            }
        except Exception as e:
            return {
                'test': 'pharmacy_nearby',
                'success': False,
                'error': str(e)
            }

    def test_medicine_diagnosis(self, disease: str, medicine_name: str) -> Dict:
        """
        Test medicine recommendation for a disease.
        
        Args:
            disease: Disease name
            medicine_name: Medicine name to recommend
            
        Returns:
            Test result dictionary
        """
        try:
            url = f"{self.api_base_url}/medicine-diagnosis"
            payload = {
                "disease": disease,
                "medicine": medicine_name
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            return {
                'test': 'medicine_diagnosis',
                'disease': disease,
                'medicine': medicine_name,
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else str(response.text)
            }
        except Exception as e:
            return {
                'test': 'medicine_diagnosis',
                'disease': disease,
                'success': False,
                'error': str(e)
            }

    def run_all_tests(self) -> List[Dict]:
        """Run all medicine-related tests."""
        print('Starting Medicine API Tests...\n')
        
        tests = [
            # Test medicine search
            self.test_medicine_search('aspirin'),
            self.test_medicine_search('paracetamol'),
            self.test_medicine_search('cough syrup'),
            
            # Test pharmacy search
            self.test_pharmacy_nearby(33.68, 73.04),
            
            # Test medicine diagnosis
            self.test_medicine_diagnosis('fever', 'aspirin'),
            self.test_medicine_diagnosis('cold', 'cough syrup'),
        ]
        
        self.test_results = tests
        return tests

    def print_results(self):
        """Print test results in a formatted way."""
        if not self.test_results:
            print("No test results available. Run 'run_all_tests()' first.")
            return
        
        passed = sum(1 for t in self.test_results if t.get('success'))
        total = len(self.test_results)
        
        print(f"\n{'='*60}")
        print(f"MEDICINE API TEST RESULTS: {passed}/{total} passed")
        print(f"{'='*60}\n")
        
        for result in self.test_results:
            status = "✓ PASS" if result.get('success') else "✗ FAIL"
            test_name = result.get('test', 'unknown')
            
            print(f"{status} | {test_name}")
            
            if result.get('medicine'):
                print(f"       Medicine: {result['medicine']}")
            if result.get('disease'):
                print(f"       Disease: {result['disease']}")
            if result.get('error'):
                print(f"       Error: {result['error']}")
            if result.get('status_code'):
                print(f"       Status: {result['status_code']}")
            
            print()

    def save_results(self, filename: str = 'medicine_test_results.json'):
        """Save test results to a JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2)
            print(f"Results saved to {filename}")
        except Exception as e:
            print(f"Error saving results: {e}")


if __name__ == '__main__':
    import sys
    
    # Create tester
    tester = MedicineResponseTester()
    
    # Run tests
    try:
        results = tester.run_all_tests()
        tester.print_results()
        tester.save_results()
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)
