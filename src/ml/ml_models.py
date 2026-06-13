# -*- coding: utf-8 -*-
"""
ML Models Training & Saving Script
Trains 6 ML models and saves them for use in the chatbot
Run once to train and save models: python src/ml/ml_models.py
"""

import pandas as pd
import numpy as np
import random
import os
import sys
import json
import joblib
from itertools import combinations
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, precision_score, recall_score, f1_score

from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression

import tensorflow as tf
from tensorflow.keras.models import Sequential, save_model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# Get the correct path to data file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "DiseaseAndSymptoms.csv")
MODELS_DIR = os.path.join(BASE_DIR, "src", "ml", "models")

# Create models directory if it doesn't exist
os.makedirs(MODELS_DIR, exist_ok=True)

print(f"[*] Loading data from: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)

print(f"[+] Dataset shape: {df.shape}")

symptom_cols = df.columns[1:]

# Expand dataset
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
print(f"[+] Expanded dataset shape: {expanded_df.shape}")

# Prepare features
mlb = MultiLabelBinarizer()
X = mlb.fit_transform(expanded_df["Symptoms"])
y = expanded_df["Disease"]
print(f"[+] Feature matrix shape: {X.shape}")

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Dictionary to store models and results
models = {}
results = {}

# Train Naive Bayes
print("\n[*] Training Naive Bayes...")
nb = MultinomialNB()
nb.fit(X_train, y_train)
pred_nb = nb.predict(X_test)
acc_nb = accuracy_score(y_test, pred_nb)
models['naive_bayes'] = nb
results['naive_bayes'] = {
    'accuracy': float(acc_nb),
    'precision': float(precision_score(y_test, pred_nb, average='weighted', zero_division=0)),
    'recall': float(recall_score(y_test, pred_nb, average='weighted', zero_division=0)),
    'f1': float(f1_score(y_test, pred_nb, average='weighted', zero_division=0))
}
print(f"[+] Naive Bayes Accuracy: {acc_nb:.4f}")

# Train Decision Tree
print("\n[*] Training Decision Tree...")
dt = DecisionTreeClassifier(max_depth=20, random_state=42)
dt.fit(X_train, y_train)
pred_dt = dt.predict(X_test)
acc_dt = accuracy_score(y_test, pred_dt)
models['decision_tree'] = dt
results['decision_tree'] = {
    'accuracy': float(acc_dt),
    'precision': float(precision_score(y_test, pred_dt, average='weighted', zero_division=0)),
    'recall': float(recall_score(y_test, pred_dt, average='weighted', zero_division=0)),
    'f1': float(f1_score(y_test, pred_dt, average='weighted', zero_division=0))
}
print(f"[+] Decision Tree Accuracy: {acc_dt:.4f}")

# Train Random Forest
print("\n[*] Training Random Forest...")
rf = RandomForestClassifier(n_estimators=50, max_depth=15, random_state=42)
rf.fit(X_train, y_train)
pred_rf = rf.predict(X_test)
acc_rf = accuracy_score(y_test, pred_rf)
models['random_forest'] = rf
results['random_forest'] = {
    'accuracy': float(acc_rf),
    'precision': float(precision_score(y_test, pred_rf, average='weighted', zero_division=0)),
    'recall': float(recall_score(y_test, pred_rf, average='weighted', zero_division=0)),
    'f1': float(f1_score(y_test, pred_rf, average='weighted', zero_division=0))
}
print(f"[+] Random Forest Accuracy: {acc_rf:.4f}")

# Train SVM
# print("\n[*] Training SVM...")
# svm = SVC(kernel='rbf', probability=True, random_state=42)
# svm.fit(X_train, y_train)
# pred_svm = svm.predict(X_test)
# acc_svm = accuracy_score(y_test, pred_svm)
# models['svm'] = svm
# results['svm'] = {
#     'accuracy': float(acc_svm),
#     'precision': float(precision_score(y_test, pred_svm, average='weighted', zero_division=0)),
#     'recall': float(recall_score(y_test, pred_svm, average='weighted', zero_division=0)),
#     'f1': float(f1_score(y_test, pred_svm, average='weighted', zero_division=0))
# }
# print(f"[+] SVM Accuracy: {acc_svm:.4f}")

# Train Logistic Regression
print("\n[*] Training Logistic Regression...")
lr = LogisticRegression(max_iter=2000, random_state=42)
lr.fit(X_train, y_train)
pred_lr = lr.predict(X_test)
acc_lr = accuracy_score(y_test, pred_lr)
models['logistic_regression'] = lr
results['logistic_regression'] = {
    'accuracy': float(acc_lr),
    'precision': float(precision_score(y_test, pred_lr, average='weighted', zero_division=0)),
    'recall': float(recall_score(y_test, pred_lr, average='weighted', zero_division=0)),
    'f1': float(f1_score(y_test, pred_lr, average='weighted', zero_division=0))
}
print(f"[+] Logistic Regression Accuracy: {acc_lr:.4f}")

# Train Neural Network
print("\n[*] Training Neural Network...")
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)
X_train_nn, X_test_nn, y_train_nn, y_test_nn = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

nn_model = Sequential([
    Dense(256, activation='relu', input_shape=(X.shape[1],)),
    Dropout(0.3),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(64, activation='relu'),
    Dropout(0.2),
    Dense(len(encoder.classes_), activation='softmax')
])

nn_model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
nn_model.fit(
    X_train_nn, y_train_nn,
    epochs=50,
    batch_size=32,
    validation_split=0.2,
    callbacks=[early_stop],
    verbose=0
)

loss, acc_nn = nn_model.evaluate(X_test_nn, y_test_nn, verbose=0)
pred_nn = np.argmax(nn_model.predict(X_test, verbose=0), axis=1)
pred_nn = encoder.inverse_transform(pred_nn)
results['neural_network'] = {
    'accuracy': float(acc_nn),
    'precision': float(precision_score(y_test, pred_nn, average='weighted', zero_division=0)),
    'recall': float(recall_score(y_test, pred_nn, average='weighted', zero_division=0)),
    'f1': float(f1_score(y_test, pred_nn, average='weighted', zero_division=0))
}
print(f"[+] Neural Network Accuracy: {acc_nn:.4f}")

# Save all models
print("\n[*] Saving models...")
joblib.dump(nb, os.path.join(MODELS_DIR, 'naive_bayes.pkl'))
joblib.dump(dt, os.path.join(MODELS_DIR, 'decision_tree.pkl'))
joblib.dump(rf, os.path.join(MODELS_DIR, 'random_forest.pkl'))
# joblib.dump(svm, os.path.join(MODELS_DIR, 'svm.pkl'))
joblib.dump(lr, os.path.join(MODELS_DIR, 'logistic_regression.pkl'))
save_model(nn_model, os.path.join(MODELS_DIR, 'neural_network.h5'))
joblib.dump(mlb, os.path.join(MODELS_DIR, 'multilabel_binarizer.pkl'))
joblib.dump(encoder, os.path.join(MODELS_DIR, 'label_encoder.pkl'))
print(f"[+] Models saved to {MODELS_DIR}")

# Save evaluation results
print("\n[*] Saving evaluation results...")
evaluation_data = {
    'timestamp': datetime.now().isoformat(),
    'dataset_size': {
        'original': len(df),
        'expanded': len(expanded_df),
        'features': X.shape[1]
    },
    'test_size': len(X_test),
    'models': results
}

results_path = os.path.join(BASE_DIR, 'data', 'chatbot_ml_results.json')
with open(results_path, 'w') as f:
    json.dump(evaluation_data, f, indent=2)
print(f"[+] Results saved to {results_path}")

print("\n" + "="*70)
print("✓ TRAINING COMPLETE")
print("="*70)
print(f"\nModels saved in: {MODELS_DIR}")
print(f"Results saved in: {results_path}")
print("\nResults Summary:")
for model_name, metrics in sorted(results.items(), key=lambda x: x[1]['accuracy'], reverse=True):
    print(f"  {model_name:25} - Accuracy: {metrics['accuracy']:.4f}")
print("\n" + "="*70)