#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask API server that wraps the orchestrator.py functionality.
Provides REST endpoints for the React frontend to interact with the local chatbot.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
import time
from werkzeug.utils import secure_filename

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import orchestrator functions - use simple version
try:
    from orchestrator_simple import analyze
except ImportError:
    # Fallback if simple version not available
    from orchestrator import analyze



# Import ML API
try:
    from src.ml.chatbot_api import register_ml_routes
    ML_ENABLED = True
    print("[API] ML models enabled")
except (ImportError, ModuleNotFoundError, Exception) as e:
    ML_ENABLED = False
    print(f"[API] ML models not available: {str(e)}")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Register ML routes if available
if ML_ENABLED:
    register_ml_routes(app)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "API server is running"}), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Process user message through the orchestrator.
    Analyzes ALL symptoms from input, not just one.
    
    Request JSON:
    {
        "message": "user's symptoms",
        "age": 30,
        "sex": "M"
    }
    
    Response JSON:
    {
        "success": true,
        "message": "input text",
        "result": {...},
        "diagnoses": [all matching diseases],
        "triage": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'message' field in request"
            }), 400
        
        message = data.get('message', '').strip()
        age = data.get('age')
        sex = data.get('sex')
        
        if not message:
            return jsonify({
                "success": False,
                "error": "Message cannot be empty"
            }), 400
        
        # Call the orchestrator analyze function
        result = analyze(transcript=message, age=age, sex=sex)
        
        # Format response
        response = {
            "success": True,
            "message": message,
            "result": result,
            # Extract key fields for easier frontend access
            "diagnoses": result.get("diagnoses", []),
            "triage": result.get("overall_triage"),
            "overall_triage": result.get("overall_triage"),
            "symptoms_extracted": result.get("symptoms_extracted", []),
            "precautions": result.get("mapped_precautions", {}),
            # Add ML and evaluation metrics
            "ml_results": result.get("ml_results"),
            "ml_comparison": result.get("ml_comparison"),
            "evaluation_metrics": result.get("evaluation_metrics", {})
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        print(f"Error in /api/chat: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Diagnostic endpoint to get symptoms list
@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    """Get list of all known symptoms"""
    try:
        from orchestrator import symptom_dict
        symptoms = list(symptom_dict.keys())
        return jsonify({
            "success": True,
            "symptoms": symptoms,
            "count": len(symptoms)
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/disease', methods=['GET'])
def get_disease():
    """Return disease information by name (query param: name)
    Example: /api/disease?name=Malaria
    """
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({"success": False, "error": "Missing 'name' query parameter"}), 400

        import orchestrator
        
        # Get disease description from knowledge base
        disease_info = orchestrator.knowledge_loader.get_disease_info(name)
        
        # Get precautions for disease
        precautions = orchestrator.precaution_loader.get_precautions(name)
        
        # Build response
        response_data = {
            "name": name,
            "description": disease_info if isinstance(disease_info, str) else f"Information about {name}",
            "symptoms": [],  # Could be populated from disease_info if structured
            "precautions": precautions if precautions else [],
            "recommendations": [
                "Consult with a qualified healthcare professional",
                "Do not self-diagnose or self-medicate",
                "Follow medical advice from licensed practitioners"
            ]
        }
        
        return jsonify({"success": True, **response_data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/health-record', methods=['POST'])
def save_health_record():
    """Save uploaded health record metadata (framework).
    Accepts JSON: { 'patient_id': str, 'title': str, 'notes': str }
    Files/uploads can be added later.
    """
    try:
        data = request.get_json() or {}
        patient_id = data.get('patient_id', 'anonymous')
        title = data.get('title', 'record')
        notes = data.get('notes', '')

        records_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'records')
        os.makedirs(records_dir, exist_ok=True)
        timestamp = int(time.time())
        filename = f"{patient_id}_{timestamp}.json"
        filepath = os.path.join(records_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({'patient_id': patient_id, 'title': title, 'notes': notes, 'created_at': timestamp}, f, ensure_ascii=False, indent=2)

        return jsonify({"success": True, "message": "Health record saved", "file": filename}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/helplines', methods=['GET'])
def helplines():
    """Return placeholder emergency contacts and helplines. Data will be provided/updated later."""
    try:
        data = {
            "emergency_numbers": [
                {"name": "Ambulance", "number": "102"},
                {"name": "Police", "number": "100"}
            ],
            "nearby_hospitals": [
                {"name": "District Hospital", "phone": "01234-567890", "distance_km": 2.1}
            ],
            "ngos": [
                {"name": "Health NGO", "phone": "09876-543210"}
            ]
        }
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Evaluation Metrics Endpoints

@app.route('/api/evaluation/metrics', methods=['GET'])
def get_evaluation_metrics():
    """Get evaluation metrics from the last analysis"""
    try:
        import orchestrator
        
        metrics = orchestrator.last_evaluation_metrics
        
        if not metrics:
            return jsonify({
                "success": False,
                "error": "No evaluation metrics available yet. Run a chat query first."
            }), 404
        
        return jsonify({
            "success": True,
            "metrics": metrics
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/evaluation/ml-performance', methods=['GET'])
def get_ml_performance():
    """Get Rule-Based Engine performance metrics"""
    try:
        import orchestrator
        
        performance = {
            'model': 'Rule-Based Engine',
            'total_diseases': len(orchestrator.symptom_dict),
            'total_symptoms': len(orchestrator.symptom_extractor.symptom_dict.get('all_symptoms', [])),
            'matching_method': 'Exact Symptom Matching',
            'description': 'Rule-based disease classification with symptom matching'
        }
        
        return jsonify({
            "success": True,
            "model_performance": performance,
            "model": "Rule-Based Engine",
            "model_type": "Traditional Rule-Based Classification"
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/evaluation/last-query', methods=['GET'])
def get_last_query_metrics():
    """Get detailed metrics from the last query"""
    try:
        import orchestrator
        
        metrics = orchestrator.last_evaluation_metrics
        
        if not metrics:
            return jsonify({
                "success": False,
                "error": "No query metrics available yet"
            }), 404
        
        return jsonify({
            "success": True,
            "query_metrics": metrics
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/evaluation/summary', methods=['GET'])
def get_evaluation_summary():
    """Get comprehensive evaluation summary"""
    try:
        import orchestrator
        
        if not orchestrator.transformer_evaluator:
            return jsonify({
                "success": False,
                "error": "Transformer Evaluator not available"
            }), 500
        
        summary = orchestrator.transformer_evaluator.get_evaluation_summary()
        
        return jsonify({
            "success": True,
            "evaluation_summary": summary
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/medicine-search', methods=['POST', 'GET'])
def medicine_search():
    """
    Search for medicines and check availability
    
    GET/POST parameters:
    - medicine_name: Name of the medicine to search
    - lat (optional): Latitude for nearby pharmacy search
    - lon (optional): Longitude for nearby pharmacy search
    """
    try:
        # Get parameters from either POST JSON or GET query
        if request.method == 'POST':
            data = request.get_json() or {}
            medicine_name = data.get('medicine_name') or data.get('medicine')
            lat = data.get('lat')
            lon = data.get('lon')
        else:
            medicine_name = request.args.get('medicine') or request.args.get('medicine_name')
            lat = request.args.get('lat')
            lon = request.args.get('lon')
        
        if not medicine_name:
            return jsonify({
                "success": False,
                "error": "Medicine name is required",
                "results": []
            }), 400
        
        # Load medicine data from CSV
        import pandas as pd
        
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'medicine_availability.csv')
        
        if not os.path.exists(csv_path):
            return jsonify({
                "success": False,
                "error": "Medicine database not found",
                "results": []
            }), 500
        
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Search for medicine (case-insensitive, partial matches)
        medicine_name_lower = medicine_name.lower().strip()
        
        # Filter results - exact match first, then partial matches
        exact_matches = df[df['medicine_name'].str.lower() == medicine_name_lower]
        partial_matches = df[
            (df['medicine_name'].str.lower().str.contains(medicine_name_lower)) & 
            (~df['medicine_name'].str.lower() == medicine_name_lower)
        ]
        
        results_df = pd.concat([exact_matches, partial_matches], ignore_index=True)
        
        if results_df.empty:
            return jsonify({
                "success": False,
                "message": f"No medicines found matching '{medicine_name}'",
                "results": []
            }), 200
        
        # Convert to structured JSON format
        results = []
        for _, row in results_df.iterrows():
            result = {
                "medicine_name": row['medicine_name'],
                "category": row.get('category', 'N/A'),
                "description": row.get('description', ''),
                "price_range": row.get('price_range', 'N/A'),
                "availability_status": row.get('availability_status', 'unknown'),
                "common_usage": row.get('common_usage', ''),
                "available": row.get('availability_status') == 'in_stock',
                "nearest_store": "Local Pharmacy",
                "distance": 2.5 if lat and lon else None,
                "price": 150,
                "store_details": {
                    "name": "Local Pharmacy",
                    "address": "Near you",
                    "phone": "+92-XXX-XXXXXX"
                }
            }
            results.append(result)
        
        return jsonify({
            "success": True,
            "message": f"Found {len(results)} medicine(s)",
            "results": results,
            "count": len(results)
        }), 200
    
    except ImportError:
        # If pandas not available, use CSV module
        import csv as csv_module
        
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'medicine_availability.csv')
        
        if not os.path.exists(csv_path):
            return jsonify({
                "success": False,
                "error": "Medicine database not found",
                "results": []
            }), 500
        
        results = []
        medicine_name_lower = medicine_name.lower().strip() if medicine_name else ""
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv_module.DictReader(f)
                for row in reader:
                    if medicine_name_lower in row.get('medicine_name', '').lower():
                        result = {
                            "medicine_name": row.get('medicine_name', ''),
                            "category": row.get('category', 'N/A'),
                            "description": row.get('description', ''),
                            "price_range": row.get('price_range', 'N/A'),
                            "availability_status": row.get('availability_status', 'unknown'),
                            "common_usage": row.get('common_usage', ''),
                            "available": row.get('availability_status') == 'in_stock',
                            "nearest_store": "Local Pharmacy",
                            "distance": 2.5 if lat and lon else None,
                            "price": 150,
                            "store_details": {
                                "name": "Local Pharmacy",
                                "address": "Near you",
                                "phone": "+92-XXX-XXXXXX"
                            }
                        }
                        results.append(result)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Error reading medicine database: {str(e)}",
                "results": []
            }), 500
        
        if not results:
            return jsonify({
                "success": False,
                "message": f"No medicines found matching '{medicine_name}'",
                "results": []
            }), 200
        
        return jsonify({
            "success": True,
            "message": f"Found {len(results)} medicine(s)",
            "results": results,
            "count": len(results)
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "results": []
        }), 500


if __name__ == '__main__':
    print("Starting Sehat Nabha API Server...")
    print("API will be available at http://localhost:5000")
    print("CORS enabled for http://localhost:3000 (Vite dev server)")
    
    # Run Flask with debug mode
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Disable reloader to avoid double-initialization
    )
