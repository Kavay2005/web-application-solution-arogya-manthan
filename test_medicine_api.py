#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Medicine Search API
Verify that the medicine search endpoint returns structured JSON data correctly.
"""

import requests
import json


def test_medicine_search():
    """Test the /api/medicine-search endpoint"""
    
    base_url = 'http://localhost:5000/api'
    
    print("=" * 60)
    print("MEDICINE SEARCH API TEST")
    print("=" * 60)
    
    # Test 1: Search via POST
    print("\n1. Testing POST request with medicine search...")
    test_medicines = [
        'Paracetamol',
        'Aspirin',
        'Ibuprofen',
        'Cough Syrup',
        'Vitamin C',
        'Antacid',
        'NonExistentMedicine'
    ]
    
    for medicine in test_medicines:
        payload = {
            "medicine_name": medicine,
            "lat": 33.68,
            "lon": 73.04
        }
        
        try:
            response = requests.post(
                f'{base_url}/medicine-search',
                json=payload,
                timeout=5
            )
            
            result = response.json()
            
            status = "✓ PASS" if response.status_code == 200 else "✗ FAIL"
            print(f"\n{status} | Medicine: {medicine}")
            print(f"   Status Code: {response.status_code}")
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message', 'N/A')}")
            print(f"   Results Count: {result.get('count', 0)}")
            
            if result.get('results'):
                for res in result['results'][:2]:  # Show first 2 results
                    print(f"   - {res.get('medicine_name')} | {res.get('category')} | {res.get('availability_status')}")
                    print(f"     Price: {res.get('price_range')} | Usage: {res.get('common_usage')}")
            
        except Exception as e:
            print(f"\n✗ ERROR | Medicine: {medicine}")
            print(f"   Error: {str(e)}")
    
    # Test 2: Search via GET
    print("\n\n2. Testing GET request with medicine search...")
    
    try:
        response = requests.get(
            f'{base_url}/medicine-search?medicine_name=Paracetamol&lat=33.68&lon=73.04',
            timeout=5
        )
        
        result = response.json()
        
        print(f"\n✓ GET Request Status: {response.status_code}")
        print(f"Response JSON Structure:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"\n✗ GET Request Error: {str(e)}")
    
    # Test 3: Verify JSON structure
    print("\n\n3. Verifying JSON Response Structure...")
    
    payload = {
        "medicine_name": "Aspirin",
        "lat": 33.68,
        "lon": 73.04
    }
    
    try:
        response = requests.post(
            f'{base_url}/medicine-search',
            json=payload,
            timeout=5
        )
        
        result = response.json()
        
        # Check required fields
        required_fields = ['success', 'message', 'results', 'count']
        missing_fields = [f for f in required_fields if f not in result]
        
        if missing_fields:
            print(f"✗ Missing fields: {missing_fields}")
        else:
            print("✓ All required root fields present")
        
        if result.get('results'):
            result_item = result['results'][0]
            required_result_fields = [
                'medicine_name',
                'category',
                'description',
                'price_range',
                'availability_status',
                'available',
                'store_details'
            ]
            
            missing_result_fields = [f for f in required_result_fields if f not in result_item]
            
            if missing_result_fields:
                print(f"✗ Missing result fields: {missing_result_fields}")
            else:
                print("✓ All required result item fields present")
                print(f"\nSample Result Item:")
                print(json.dumps(result_item, indent=2))
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)


if __name__ == '__main__':
    test_medicine_search()
