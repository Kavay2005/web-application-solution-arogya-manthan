# Quick Start Guide - Transformer-Based Sehat Nabha

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies (2 minutes)
**Windows:**
```bash
install_transformer_deps.bat
```

**macOS/Linux:**
```bash
python install_transformer_deps.py
```

Or manually:
```bash
pip install -r requirements.txt
```

### Step 2: Start the API Server (1 minute)
```bash
python api_server.py
```

You'll see:
```
[Transformer Classifier] Device: cpu
✓ DistilBERT loaded successfully
✓ RoBERTa loaded successfully  
✓ BERT loaded successfully
Initializing Sehat Nabha orchestrator...
```

### Step 3: Start the Frontend (1 minute)
In a new terminal:
```bash
npm run dev
```

### Step 4: Open in Browser (1 minute)
Navigate to: **http://localhost:3000**

---

## 💡 First Test

1. **Login** with any phone number (e.g., 9876543210)
2. **Type symptoms**: "I have high fever, cough, and sore throat"
3. **View Results**: 
   - Diseases predicted by rule-based engine
   - Predictions from DistilBERT, RoBERTa, BERT
4. **Click Metrics Button**: "📊 View Research Metrics"
5. **See Detailed Stats**:
   - Model predictions
   - Confidence scores  
   - Model agreement
   - KPE (Entropy) values
   - KDE (Density) values

---

## 📊 What to Look For

### Good Results
✅ All 3 models predict the same disease  
✅ Model agreement > 95%  
✅ Confidence scores > 0.8  
✅ KPE values low (models are confident)

### Expected Behavior
- Rule-based: Only exact symptom matches
- Transformers: Understand similar/partial symptoms
- Transformers usually give more results

---

## 🛠️ If Something Goes Wrong

### "No module named 'transformers'"
```bash
pip install transformers>=4.30.0 torch>=2.0.0
```

### "CUDA out of memory"
Change in `api_server.py` startup:
```python
use_gpu=False  # Use CPU instead
```

### Models downloading very slowly
- Normal on first run (2GB download)
- Wait 5-15 minutes depending on speed
- Models are cached after first download

### Port 5000 already in use
```bash
python api_server.py --port 5001
```

---

## 📝 For Your Research Paper

The metrics displayed include everything needed:

**Section 1: Model Performance**
- Accuracy, Precision, Recall, F1-Score
- Copy from "📊 View Research Metrics"

**Section 2: Evaluation Metrics**
- KPE (Kernel Probability Entropy)
- KDE (Kernel Density Estimation)
- Model Agreement Score
- Confidence per model

**Section 3: Comparison**
- Rule-based vs Transformer results
- Shown side-by-side in metrics panel

---

## 🎯 Key Differences from Previous Version

### Before (Traditional ML)
```
Input: "fever, cough"
↓ 
Exact Match: Looking for diseases with BOTH
↓
Result: Pneumonia, Influenza
```

### Now (Transformers)
```
Input: "fever, cough"
↓
Understanding: High temperature + respiratory issue
↓
Result: Pneumonia, Influenza, COVID, Bronchitis, Asthma
(More results due to semantic understanding)
```

---

## 📚 Three Models Explained

### DistilBERT ⚡ (Fastest)
- 40% smaller than BERT
- Runs on any computer
- Best for real-time responses
- Good for production

### RoBERTa 🎯 (Best Balanced)
- Better than BERT on classification
- More robust to variations
- Medium speed/accuracy tradeoff
- Recommended for medical use

### BERT 🧠 (Most Accurate)
- Industry standard
- Highest accuracy
- Requires more CPU/RAM
- Best for offline analysis

**Final Prediction = Majority vote of all 3**

---

## 🔍 Understanding the Metrics

### Model Predictions
Shows what each transformer predicted:
- DistilBERT: Pneumonia (confidence: 0.89)
- RoBERTa: Pneumonia (confidence: 0.92)
- BERT: Pneumonia (confidence: 0.94)

### Model Agreement
Shows consensus:
- 3/3 models agree = 100% ✓
- 2/3 models agree = 67% ⚠️
- 1/3 models agree = 33% ✗

### Confidence Scores
Per-model confidence (0-100%):
- Above 80% = High confidence
- 50-80% = Medium confidence  
- Below 50% = Low confidence

### KPE (Entropy)
How uncertain the model is:
- Lower = More confident
- Higher = Less confident

### KDE (Density)
Probability distribution quality:
- Higher = Better distribution
- Lower = Concentrated predictions

---

## 💾 Data Collection for Paper

### Take Screenshots
1. Run a test case
2. View metrics
3. Screenshot the panel
4. Use in paper's results section

### Export Results
Metrics are returned as JSON from API:
```
GET /api/evaluation/last-query
GET /api/evaluation/ml-performance
GET /api/evaluation/summary
```

### Save Test Cases
Test different inputs and collect results:
1. Simple cases (1-2 symptoms)
2. Complex cases (5+ symptoms)
3. Edge cases (ambiguous symptoms)
4. Conflicting symptoms

---

## 🎓 For Your Research

**Recommended Test Set:**
- 20-30 test cases
- Mix of common and rare diseases
- Various symptom combinations
- Different language styles

**Metrics to Include in Paper:**
- Accuracy per model: ✓
- Precision/Recall: ✓
- F1-Score: ✓  
- Confusion Matrix: ✓
- KPE Analysis: ✓
- KDE Analysis: ✓
- Model Comparison: ✓
- Ensemble Performance: ✓

---

## 📞 Need Help?

1. Check console output for errors
2. Read `TRANSFORMER_README.md` for detailed info
3. Check requirements are installed: `pip list`
4. Ensure Python 3.8+: `python --version`

---

**Remember**: First run takes 5-10 minutes to download models. This is normal!  
**Status**: Ready for research & production use ✅
