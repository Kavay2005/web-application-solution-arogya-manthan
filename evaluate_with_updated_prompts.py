#!/usr/bin/env python3
"""
Unified Evaluation Script using updated_eval_prompts.csv
- First 50 rows: Medicine Availability Module
- Next 50 rows: Chatbot Module
"""

import requests
import time
import sys
from pathlib import Path

try:
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
    import pandas as pd
except ImportError:
    print("ERROR: Required packages not found.")
    sys.exit(1)

MEDICINE_API_URL = "http://127.0.0.1:5000/api/medicine-search"
CHATBOT_API_URL = "http://127.0.0.1:5000/api/chat"

# ============================================================================
# MEDICINE EVALUATION (First 50 rows)
# ============================================================================

def call_medicine_search(medicine):
    """Call the medicine search API"""
    try:
        params = {
            "medicine": medicine,
            "lat": 33.6844,  # Islamabad
            "lon": 73.0479
        }
        response = requests.get(MEDICINE_API_URL, params=params, timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

def extract_medicine_label(response):
    """Extract if medicine is available"""
    try:
        if not response.get("success"):
            return "Not Available"
        
        result = response.get("result", {})
        if isinstance(result, dict):
            pharmacies = result.get("pharmacies", [])
            if pharmacies and len(pharmacies) > 0:
                return "Available"
        
        return "Not Available"
    except:
        return "Not Available"

def evaluate_medicine():
    """Evaluate medicine availability module"""
    print("=" * 80)
    print("MEDICINE AVAILABILITY MODULE EVALUATION")
    print("=" * 80)
    
    # Load first 50 rows
    csv_path = Path("updated_eval_prompts.csv")
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found")
        sys.exit(1)
    
    df = pd.read_csv(csv_path)
    medicine_df = df[df['module'] == 'medicine'].head(50)
    print(f"\nLoaded {len(medicine_df)} medicine test prompts")
    
    y_true = []
    y_pred = []
    results = []
    
    print("\nRunning medicine evaluations...")
    for i, row in medicine_df.iterrows():
        medicine = row['query']
        expected_label = "Available"  # Default to Available for available medicines
        
        # Call API
        api_response = call_medicine_search(medicine)
        predicted_label = extract_medicine_label(api_response)
        
        y_true.append(expected_label)
        y_pred.append(predicted_label)
        
        results.append({
            "prompt_id": row['prompt_id'],
            "medicine": medicine,
            "expected": expected_label,
            "predicted": predicted_label,
            "correct": expected_label == predicted_label,
            "pharmacies_found": len(api_response.get("result", {}).get("pharmacies", []))
        })
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(medicine_df)} prompts...")
        
        time.sleep(0.1)
    
    # Save results
    pd.DataFrame(results).to_csv("medicine_eval_results.csv", index=False)
    print(f"✓ Results saved to medicine_eval_results.csv")
    
    # Calculate metrics
    accuracy = accuracy_score(y_true, y_pred)
    labels = sorted(list(set(y_true + y_pred)))
    
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average=None, zero_division=0
    )
    
    weighted_precision = sum(p * s for p, s in zip(precision, support)) / sum(support)
    weighted_recall = sum(r * s for r, s in zip(recall, support)) / sum(support)
    weighted_f1 = sum(f * s for f, s in zip(f1, support)) / sum(support)
    
    print("\n" + "=" * 80)
    print("MEDICINE AVAILABILITY RESULTS")
    print("=" * 80)
    print(f"\nAccuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"Precision (Weighted): {weighted_precision:.4f}")
    print(f"Recall (Weighted): {weighted_recall:.4f}")
    print(f"F1-Score (Weighted): {weighted_f1:.4f}")
    
    correct = len([r for r in results if r['correct']])
    print(f"\nCorrect: {correct}/{len(results)}")
    
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    print("\nConfusion Matrix:")
    print(f"{'':20s}", end="")
    for label in labels:
        print(f"\t{label}", end="")
    print()
    for i, label in enumerate(labels):
        print(f"{label:<20s}", end="")
        for j in range(len(labels)):
            print(f"\t{cm[i][j]}", end="")
        print()
    
    return {
        "accuracy": accuracy,
        "precision": weighted_precision,
        "recall": weighted_recall,
        "f1": weighted_f1,
        "correct": correct,
        "total": len(results)
    }

# ============================================================================
# CHATBOT EVALUATION (Rows 51-100)
# ============================================================================

def call_chatbot(query):
    """Call the chatbot API"""
    try:
        payload = {"message": query, "language": "en"}
        response = requests.post(CHATBOT_API_URL, json=payload, timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

def extract_chatbot_label(response):
    """Extract predicted disease from chatbot response"""
    try:
        if not response.get("success"):
            return "Unknown"
        
        result = response.get("result", {})
        if isinstance(result, dict):
            diagnoses = result.get("diagnoses", [])
            if diagnoses and len(diagnoses) > 0:
                return diagnoses[0].get("name", "Unknown")
        
        return "Unknown"
    except:
        return "Unknown"

def evaluate_chatbot():
    """Evaluate chatbot module"""
    print("\n" + "=" * 80)
    print("CHATBOT MODULE EVALUATION")
    print("=" * 80)
    
    csv_path = Path("updated_eval_prompts.csv")
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found")
        return None
    
    df = pd.read_csv(csv_path)
    chatbot_df = df[df['module'] == 'chatbot'].head(50)
    print(f"\nLoaded {len(chatbot_df)} chatbot test prompts")
    
    y_true = []
    y_pred = []
    results = []
    
    print("\nRunning chatbot evaluations...")
    for i, row in chatbot_df.iterrows():
        query = row['query']
        expected_label = row['expected_label'] if pd.notna(row['expected_label']) else "Unknown"
        
        # Call API
        api_response = call_chatbot(query)
        predicted_label = extract_chatbot_label(api_response)
        
        y_true.append(expected_label)
        y_pred.append(predicted_label)
        
        results.append({
            "prompt_id": row['prompt_id'],
            "query": query,
            "expected": expected_label,
            "predicted": predicted_label,
            "correct": expected_label == predicted_label
        })
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(chatbot_df)} prompts...")
        
        time.sleep(0.1)
    
    # Save results
    pd.DataFrame(results).to_csv("chatbot_eval_results.csv", index=False)
    print(f"✓ Results saved to chatbot_eval_results.csv")
    
    # Calculate metrics
    accuracy = accuracy_score(y_true, y_pred)
    labels = sorted(list(set(y_true + y_pred)))
    
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average=None, zero_division=0
    )
    
    weighted_precision = sum(p * s for p, s in zip(precision, support)) / sum(support)
    weighted_recall = sum(r * s for r, s in zip(recall, support)) / sum(support)
    weighted_f1 = sum(f * s for f, s in zip(f1, support)) / sum(support)
    
    print("\n" + "=" * 80)
    print("CHATBOT RESULTS")
    print("=" * 80)
    print(f"\nAccuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"Precision (Weighted): {weighted_precision:.4f}")
    print(f"Recall (Weighted): {weighted_recall:.4f}")
    print(f"F1-Score (Weighted): {weighted_f1:.4f}")
    
    correct = len([r for r in results if r['correct']])
    print(f"\nCorrect: {correct}/{len(results)}")
    
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    print("\nConfusion Matrix:")
    print(f"{'':20s}", end="")
    for label in labels:
        print(f"\t{label[:10]}", end="")
    print()
    for i, label in enumerate(labels):
        print(f"{label[:20]:<20s}", end="")
        for j in range(len(labels)):
            print(f"\t{cm[i][j]}", end="")
        print()
    
    return {
        "accuracy": accuracy,
        "precision": weighted_precision,
        "recall": weighted_recall,
        "f1": weighted_f1,
        "correct": correct,
        "total": len(results)
    }

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Check API availability
    print("\nChecking API availability...")
    try:
        requests.get(MEDICINE_API_URL, params={"medicine": "test", "lat": 33.68, "lon": 73.04}, timeout=5)
        requests.post(CHATBOT_API_URL, json={"message": "test"}, timeout=5)
        print("✓ Both APIs are accessible")
    except:
        print("✗ Cannot reach APIs. Make sure Flask server is running.")
        sys.exit(1)
    
    # Run evaluations
    med_results = evaluate_medicine()
    chat_results = evaluate_chatbot()
    
    # Summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    print("\n| Module | Accuracy | Precision | Recall | F1-Score |")
    print("|--------|----------|-----------|--------|----------|")
    if med_results:
        print(f"| Medicine | {med_results['accuracy']:.4f} | {med_results['precision']:.4f} | {med_results['recall']:.4f} | {med_results['f1']:.4f} |")
    if chat_results:
        print(f"| Chatbot | {chat_results['accuracy']:.4f} | {chat_results['precision']:.4f} | {chat_results['recall']:.4f} | {chat_results['f1']:.4f} |")
    
    print("\nEvaluation complete!")
