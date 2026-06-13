from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import joblib
import os
import sys
import random
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import load_model

# Get paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_PATH = os.path.join(BASE_DIR, "data", "DiseaseAndSymptoms.csv")
MODELS_DIR = os.path.dirname(os.path.abspath(__file__))

def load_all_models():
    """Load all saved ML models"""
    models = {}
    
    # Load sklearn models
    sklearn_models = ['naive_bayes', 'decision_tree', 'random_forest', 'logistic_regression']
    for model_name in sklearn_models:
        model_path = os.path.join(MODELS_DIR, f'{model_name}.pkl')
        if os.path.exists(model_path):
            models[model_name] = joblib.load(model_path)
            print(f"[+] Loaded {model_name}")
    
    # Load neural network
    nn_path = os.path.join(MODELS_DIR, 'neural_network.h5')
    if os.path.exists(nn_path):
        models['neural_network'] = load_model(nn_path)
        print(f"[+] Loaded neural_network")
    
    return models

def prepare_test_data():
    """Prepare test data same way as training"""
    print(f"\n[*] Loading data from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    
    # Expand dataset (same way as training)
    print("[*] Expanding dataset with synthetic samples...")
    expanded = []
    samples_per_disease = 150
    
    for _, row in df.iterrows():
        disease = row["Disease"]
        symptoms = [s for s in row[1:] if pd.notna(s)]
        
        for _ in range(samples_per_disease):
            k = random.randint(1, len(symptoms))
            subset = random.sample(symptoms, k)
            expanded.append({
                "Disease": disease,
                "Symptoms": subset
            })
    
    expanded_df = pd.DataFrame(expanded)
    
    # Save expanded dataset to CSV
    expanded_data_path = os.path.join(BASE_DIR, "data", "newDiseaseAndSymptom.csv")
    expanded_df.to_csv(expanded_data_path, index=False)
    print(f"[+] Expanded dataset saved to: {expanded_data_path}")
    
    # Load MultiLabelBinarizer
    mlb_path = os.path.join(MODELS_DIR, 'multilabel_binarizer.pkl')
    mlb = joblib.load(mlb_path)
    
    X = mlb.transform(expanded_df["Symptoms"])
    y = expanded_df["Disease"]
    
    # Split same way as training
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"[+] Test set size: {len(X_test)}")
    return X_test, y_test, mlb

def evaluate_all_models():
    """Evaluate all saved models and generate results"""
    print("\n" + "="*70)
    print("EVALUATING ALL SAVED MODELS")
    print("="*70)
    
    # Load models
    models = load_all_models()
    if not models:
        print("[-] No models found!")
        return
    
    # Prepare data
    X_test, y_test, mlb = prepare_test_data()
    
    # Load label encoder for neural network
    encoder_path = os.path.join(MODELS_DIR, 'label_encoder.pkl')
    encoder = joblib.load(encoder_path)
    
    results = {}
    predictions = {}
    
    print("\n[*] Evaluating models...")
    print("-" * 70)
    
    # Evaluate each model
    for model_name, model in models.items():
        print(f"\nEvaluating {model_name}...")
        
        try:
            if model_name == 'neural_network':
                # Neural network prediction
                y_pred_encoded = np.argmax(model.predict(X_test, verbose=0), axis=1)
                y_pred = encoder.inverse_transform(y_pred_encoded)
            else:
                # Sklearn models
                y_pred = model.predict(X_test)
            
            predictions[model_name] = y_pred
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
            
            results[model_name] = {
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1': float(f1)
            }
            
            print(f"  ✓ Accuracy:  {accuracy:.4f}")
            print(f"  ✓ Precision: {precision:.4f}")
            print(f"  ✓ Recall:    {recall:.4f}")
            print(f"  ✓ F1-Score:  {f1:.4f}")
            
        except Exception as e:
            print(f"  [-] Error evaluating {model_name}: {str(e)}")
    
    # Display summary
    print("\n" + "="*70)
    print("SUMMARY - Models Ranked by Accuracy")
    print("="*70)
    for model_name, metrics in sorted(results.items(), key=lambda x: x[1]['accuracy'], reverse=True):
        print(f"{model_name:25} - Accuracy: {metrics['accuracy']:.4f} | F1: {metrics['f1']:.4f}")
    
    return results, predictions, y_test

def plot_confusion_matrix(y_true, y_pred, model_name="Model"):
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(14, 11))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=np.unique(y_true))
    disp.plot(cmap='Blues', ax=ax, values_format='d')
    plt.title(f"Confusion Matrix - {model_name}", fontsize=20, fontweight='bold')
    plt.xlabel('Predicted Label', fontsize=17)
    plt.ylabel('True Label', fontsize=17)
    ax.tick_params(axis='both', labelsize=14)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    plt.tight_layout()
    plt.show()

def plot_algorithm_accuracy(results):
    models = list(results.keys())
    accuracy = [results[m]["accuracy"] for m in models]
    
    plt.figure(figsize=(22, 16))
    bars = plt.bar(models, accuracy, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'], width=0.6)
    plt.xlabel("Algorithms", fontsize=16)
    plt.ylabel("Accuracy", fontsize=16)
    plt.title("Algorithm Accuracy Comparison", fontsize=19, fontweight='bold')
    plt.xticks(rotation=90, ha='right', fontsize=16)
    plt.yticks(fontsize=16)
    plt.ylim([0, 1.1])
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}', ha='center', va='bottom', fontsize=17, fontweight='bold')
    
    plt.tight_layout()
    plt.show()

def plot_all_metrics(results):
    """Plot all metrics for comparison"""
    models = list(results.keys())
    accuracy = [results[m]["accuracy"] for m in models]
    precision = [results[m]["precision"] for m in models]
    recall = [results[m]["recall"] for m in models]
    f1 = [results[m]["f1"] for m in models]
    
    x = np.arange(len(models))
    width = 0.2
    
    plt.figure(figsize=(20, 10))
    bars1 = plt.bar(x - 1.5*width, accuracy, width, label='Accuracy')
    bars2 = plt.bar(x - 0.5*width, precision, width, label='Precision')
    bars3 = plt.bar(x + 0.5*width, recall, width, label='Recall')
    bars4 = plt.bar(x + 1.5*width, f1, width, label='F1-Score')
    
    # Add value labels on all bars
    for bars in [bars1, bars2, bars3, bars4]:
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=26, fontweight=300, rotation=90)
    
    plt.xlabel("Models", fontsize=37)
    plt.ylabel("Score", fontsize=37)
    # plt.title("Model Performance Metrics Comparison", fontsize=37, fontweight='bold')
    plt.xticks(x, models, rotation=90, ha='right', fontsize=30)
    plt.yticks(fontsize=34)
    plt.legend(loc='upper center', ncol=4, bbox_to_anchor=(0.5, 1.15), fontsize=24, frameon=True)
    plt.ylim([0, 1.15])
    plt.tight_layout()
    plt.show()

def plot_training_accuracy(history):
    plt.figure()
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('Training Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'])
    plt.show()

if __name__ == "__main__":
    # Run evaluation on all models
    results, predictions, y_test = evaluate_all_models()
    
    print("\n[*] Generating visualizations...")
    
    # Plot accuracy comparison
    # plot_algorithm_accuracy(results)
    
    # Plot all metrics
    plot_all_metrics(results)
    
    # Plot confusion matrices for all models
    # for model_name, metrics in sorted(results.items(), key=lambda x: x[1]['accuracy'], reverse=True):
    #     plot_confusion_matrix(y_test, predictions[model_name], model_name)
    
    print("\n[+] Evaluation complete!")