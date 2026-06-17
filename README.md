<div align="center">

# 🛡️ CyberShield ML Detection

### ML-Powered Network Intrusion Detection System

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?style=flat-square&logo=streamlit)](https://streamlit.io)
[![Dataset](https://img.shields.io/badge/Dataset-CIC--IDS2017-green?style=flat-square)](https://www.unb.ca/cic/datasets/ids-2017.html)
[![License](https://img.shields.io/badge/License-Academic-orange?style=flat-square)]()

*Graduation Project — Machine Learning & Big Data Course*

</div>

---

## 📌 What Is This?

**CyberShield ML Detection** is a machine learning-based **Network Intrusion Detection System (NIDS)** built entirely in Python. It trains and compares three machine learning classifiers on the real-world **CIC-IDS2017** network traffic dataset, classifying flows as `BENIGN` or attack traffic with full performance analysis through an interactive 4-tab dashboard.

---

## ✨ Features

| Feature | Details |
|---|---|
| **3 ML Models** | Random Forest · XGBoost · LightGBM |
| **5-Fold CV** | Stratified Cross-Validation — no data leakage |
| **Binary + Multiclass** | BENIGN vs ATTACK, or all 14 attack types separately |
| **Model Comparison** | Radar chart, ROC curves, ranked performance table |
| **Attack Analytics** | Class distribution, feature profiles, correlation heatmap |
| **Dataset** | CIC-IDS2017 — University of New Brunswick |
| **Auto-Save** | Trained models saved automatically as `.joblib` files |

---

## 🗂️ Project Structure

```
CyberShield_ML_Detection/
│
├── app.py                    ← Main entry point — run this file
├── config.py                 ← All settings, label maps, constants
├── requirements.txt          ← All Python dependencies
├── README.md
│
├── pipeline/
│   ├── loader.py             ← CSV loading with encoding fallback
│   └── preprocessor.py      ← Clean, engineer, and scale features
│
├── models/
│   ├── trainer.py            ← Train 3 models with 5-Fold CV
│   └── evaluator.py          ← Metrics, ROC curves, confusion matrix
│
├── saved_models/             ← Auto-saved trained models (.joblib)
│   ├── lightgbm.joblib
│   ├── xgboost.joblib
│   └── random_forest.joblib
│
└── dashboard/
    ├── styles.py             ← Dark theme CSS
    ├── overview.py           ← Tab 1: Dataset overview
    ├── training.py           ← Tab 2: Model training
    ├── comparison.py         ← Tab 3: Model comparison
    └── analytics.py          ← Tab 4: Attack analytics
```

---

## ⚙️ Tech Stack

```
Python 3.10+      Core language
Streamlit         Interactive web dashboard
Pandas / NumPy    Data loading and processing
Scikit-learn      ML pipeline, CV, metrics, StandardScaler
XGBoost           Gradient boosting classifier
LightGBM          Fast gradient boosting — best model
Plotly            Interactive charts and visualizations
Joblib            Model serialization to disk
```

---

## 🚀 Quick Start

### Step 1 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Run the App
```bash
streamlit run app.py
```

### Step 3 — Open in Browser
```
http://localhost:8501
```

---

## 📋 Usage Workflow

```
1️⃣  Overview Tab
    └── Upload CIC-IDS2017 CSV file
    └── Set sample size (10,000 – 100,000 rows)
    └── Click Load Dataset
    └── Inspect class distribution and feature stats

2️⃣  Model Training Tab
    └── Choose mode: Binary or Multiclass
    └── Click Train All 3 Models
    └── Wait 2–5 minutes
    └── Review CV results and hold-out metrics

3️⃣  Model Comparison Tab
    └── Compare all 3 models on radar chart
    └── View ROC curves overlay
    └── See ranked performance table

4️⃣  Attack Analytics Tab
    └── Explore BENIGN vs Attack distribution
    └── View feature profiles per attack type
    └── Analyze correlation heatmap
```

---

## 📊 Model Performance (CIC-IDS2017)

| Rank | Model | Accuracy | F1-Score | AUC-ROC | Train Time |
|:---:|---|:---:|:---:|:---:|:---:|
| 🥇 | **LightGBM** | 99.97% | 99.97% | 99.99% | 4.7s |
| 🥈 | **XGBoost** | 99.95% | 99.96% | 99.99% | 14.2s |
| 🥉 | **Random Forest** | 99.94% | 99.95% | 99.99% | 20.5s |

> Results based on Stratified 5-Fold Cross-Validation on CIC-IDS2017.

---

## 📁 Dataset

| Property | Value |
|---|---|
| Name | CIC-IDS2017 |
| Source | University of New Brunswick (UNB) |
| URL | https://www.unb.ca/cic/datasets/ids-2017.html |
| Total Flows | 2.8 Million |
| Features | 79 columns per flow |
| Attack Types | 14 categories |
| Recommended File | `Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv` |

---

## 🧪 ML Pipeline

```
Raw CSV
   │
   ▼
Label Normalisation     → Map raw labels to unified names
   │
   ▼
Feature Engineering     → Add Packet_Ratio, Total_Bytes, Bytes_Ratio
   │
   ▼
Infinity / NaN Fix      → Replace inf with 0, fill missing with 0
   │
   ▼
Zero-Variance Removal   → Drop constant columns
   │
   ▼
StandardScaler          → Scale all features to mean=0, std=1
   │
   ▼
Stratified 5-Fold CV    → Train + evaluate without data leakage
   │
   ▼
Final Model             → Train on full dataset → save to disk
```

---

## 📚 Dashboard Tabs

| Tab | Purpose |
|---|---|
| 🏠 **Overview** | Upload dataset, view class distribution, feature statistics |
| 🤖 **Model Training** | Train all 3 models, view CV scores and hold-out metrics |
| 📊 **Model Comparison** | Radar chart, ROC curve overlay, ranked table |
| 📈 **Attack Analytics** | Traffic treemap, feature distributions, correlation heatmap |

---

## 📄 License

Academic use only. Dataset courtesy of the **Canadian Institute for Cybersecurity**, University of New Brunswick.

---

<div align="center">

**CyberShield ML Detection** — *Machine Learning & Big Data*  Project 2025/2026

</div>
