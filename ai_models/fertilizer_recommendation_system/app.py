"""
app.py - Streamlit Fertilizer Recommendation Dashboard
Run: streamlit run app.py
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR  = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)

from fertilizer_service import (predict_fertilizer, get_soil_types, get_crop_types,
                                  soil_health_check, get_organic_suggestions,
                                  get_overuse_warnings, FERTILIZER_INFO)
from preprocess import load_data, clean_data
from utils import (plot_fertilizer_distribution, plot_correlation_heatmap,
                   plot_soil_nutrient_analysis, plot_crop_vs_fertilizer)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🌾 FertilizerAI – Kisaan Mitra",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background-color: #0f1b12;}
[data-testid="stSidebar"] {background-color: #1a2f1e;}
h1, h2, h3 {color: #76c442;}
.metric-card {
    background: linear-gradient(135deg, #1e3a22, #2a5232);
    border-radius: 12px; padding: 20px; text-align: center;
    border: 1px solid #3a6b42; margin: 8px 0;
}
.metric-value {font-size: 2rem; font-weight: 700; color: #76c442;}
.metric-label {font-size: 0.85rem; color: #a8d5a2; margin-top: 4px;}
.result-card {
    background: linear-gradient(135deg, #1a3a1e, #204020);
    border-radius: 16px; padding: 28px; text-align: center;
    border: 2px solid #4CAF50; margin: 16px 0;
}
.result-fertilizer {font-size: 2.5rem; font-weight: 800; color: #76c442;}
.result-conf {font-size: 1.2rem; color: #a8d5a2; margin-top: 8px;}
</style>
""", unsafe_allow_html=True)

# ── Sidebar Navigation ────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/wheat.png", width=80)
st.sidebar.title("🌾 FertilizerAI")
st.sidebar.markdown("*Kisaan Mitra – Smart Agriculture*")
st.sidebar.divider()

page = st.sidebar.radio("📌 Navigate", [
    "🏠 Home",
    "🔮 Predict Fertilizer",
    "📊 Model Performance",
    "📈 Dataset Analysis",
    "ℹ️ About",
])

# ── Helper: load df ───────────────────────────────────────────────────────────
@st.cache_data
def get_df():
    df = load_data()
    return clean_data(df)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────────────────────────────────────────
if page == "🏠 Home":
    st.title("🌾 AI-Powered Fertilizer Recommendation System")
    st.markdown("##### Smart, Sustainable, Soil-Optimized Farming")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-value">7</div><div class="metric-label">Fertilizer Classes</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-value">99</div><div class="metric-label">Training Samples</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-value">7</div><div class="metric-label">ML Models</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><div class="metric-value">8</div><div class="metric-label">Input Features</div></div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("✨ Features")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
- 🤖 7 ML Algorithms compared automatically
- 🏆 Best model auto-selected & saved
- 🌱 Soil health analysis included
- ♻️ Organic fertilizer alternatives
        """)
    with col2:
        st.markdown("""
- ⚠️ Overuse & toxicity warnings
- 🌾 Crop-specific recommendations
- 📊 Confidence score per prediction
- 🌍 Sustainable farming tips
        """)

    st.divider()
    st.subheader("🌱 Supported Fertilizers")
    cols = st.columns(4)
    for i, (name, info) in enumerate(FERTILIZER_INFO.items()):
        with cols[i % 4]:
            st.markdown(f"**{info['icon']} {name}**  \n`{info['npk']}`  \n{info['description'][:60]}…")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PREDICT FERTILIZER
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔮 Predict Fertilizer":
    st.title("🔮 Predict Best Fertilizer")
    st.markdown("Fill in your soil and crop details to get an instant AI recommendation.")
    st.divider()

    models_dir = os.path.join(BASE_DIR, "models")
    if not os.path.exists(os.path.join(models_dir, "best_fertilizer_model.pkl")):
        st.error("⚠️ Model not trained yet! Run `python train_pipeline.py` first.")
        st.stop()

    soil_types = get_soil_types()
    crop_types = get_crop_types()

    with st.form("predict_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            temperature  = st.slider("🌡️ Temperature (°C)", 20, 45, 30)
            humidity     = st.slider("💧 Humidity (%)",     45, 75, 55)
            moisture     = st.slider("🌊 Moisture (%)",     25, 70, 45)
        with col2:
            soil_type    = st.selectbox("🪨 Soil Type", soil_types)
            crop_type    = st.selectbox("🌾 Crop Type", crop_types)
        with col3:
            nitrogen     = st.slider("🟢 Nitrogen",     0, 50, 20)
            potassium    = st.slider("🟠 Potassium",    0, 25, 5)
            phosphorous  = st.slider("🔵 Phosphorous",  0, 45, 15)

        submitted = st.form_submit_button("🚀 Get Recommendation", use_container_width=True)

    if submitted:
        try:
            fertilizer, confidence, info, model_name = predict_fertilizer(
                temperature, humidity, moisture,
                soil_type, crop_type,
                nitrogen, potassium, phosphorous
            )

            # Result card
            st.markdown(f"""
<div class="result-card">
  <div style="font-size:3rem">{info.get('icon','🌱')}</div>
  <div class="result-fertilizer">{fertilizer}</div>
  <div class="result-conf">NPK Ratio: {info.get('npk','N/A')}</div>
  <div class="result-conf">Confidence: {confidence*100:.1f}%</div>
  <div class="result-conf" style="color:#8bc34a;margin-top:12px">{info.get('description','')}</div>
</div>
""", unsafe_allow_html=True)

            # Confidence bar
            st.progress(confidence)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("💡 Usage Tip")
                st.info(info.get("tip", "Apply as per soil test results."))

                st.subheader("♻️ Organic Alternatives")
                for alt in get_organic_suggestions(fertilizer):
                    st.success(f"🌿 {alt}")

            with col2:
                st.subheader("🌱 Soil Health Check")
                health = soil_health_check(nitrogen, potassium, phosphorous)
                st.metric("Health Score", f"{health['score']}/100", health["label"])
                for issue in health["issues"]:
                    st.warning(issue)
                for sug in health["suggestions"]:
                    st.info(sug)

                warnings = get_overuse_warnings(nitrogen, potassium, phosphorous)
                if warnings:
                    st.subheader("⚠️ Overuse Warnings")
                    for w in warnings:
                        st.error(w)

            st.caption(f"🤖 Model used: {model_name}")

        except Exception as e:
            st.error(f"Prediction failed: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: MODEL PERFORMANCE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📊 Model Performance":
    st.title("📊 Model Performance")
    graphs_dir = os.path.join(BASE_DIR, "outputs", "graphs")

    for img_name, caption in [
        ("model_comparison.png",   "Model Accuracy vs Cross-Validation Score"),
        ("confusion_matrix.png",   "Confusion Matrix – Best Model"),
        ("feature_importance.png", "Feature Importance"),
    ]:
        path = os.path.join(graphs_dir, img_name)
        if os.path.exists(path):
            st.subheader(caption)
            st.image(path, use_column_width=True)
        else:
            st.warning(f"'{img_name}' not found. Run train_pipeline.py first.")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: DATASET ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📈 Dataset Analysis":
    st.title("📈 Dataset Analysis")
    df = get_df()

    st.subheader("📋 Raw Data Preview")
    st.dataframe(df.head(20), use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows",    df.shape[0])
    col2.metric("Total Columns", df.shape[1])
    col3.metric("Fertilizer Classes", df["Fertilizer Name"].nunique())

    graphs_dir = os.path.join(BASE_DIR, "outputs", "graphs")
    for img_name, caption in [
        ("fertilizer_distribution.png", "Fertilizer Distribution"),
        ("correlation_heatmap.png",      "Correlation Heatmap"),
        ("soil_nutrient_analysis.png",   "Soil Nutrient Analysis"),
        ("crop_vs_fertilizer.png",       "Crop vs Fertilizer"),
        ("temp_moisture_scatter.png",    "Temperature vs Moisture"),
    ]:
        path = os.path.join(graphs_dir, img_name)
        if os.path.exists(path):
            st.subheader(caption)
            st.image(path, use_column_width=True)
        else:
            st.info(f"Run train_pipeline.py to generate '{img_name}'")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ABOUT
# ─────────────────────────────────────────────────────────────────────────────
elif page == "ℹ️ About":
    st.title("ℹ️ About FertilizerAI")
    st.markdown("""
### 🌾 Kisaan Mitra – Fertilizer Recommendation System

This AI-powered system was built to help Indian farmers make data-driven fertilizer decisions.

**Dataset**: Fertilizer Prediction.csv (99 samples, 7 fertilizer classes)

**Models Trained**:
| Model | Notes |
|-------|-------|
| Random Forest | Ensemble, handles non-linearity |
| Decision Tree | Interpretable |
| XGBoost | High performance gradient boosting |
| SVM | Good with small datasets |
| KNN | Distance-based |
| Logistic Regression | Baseline |
| Naive Bayes | Fast probabilistic |

**Tech Stack**: Python · Scikit-learn · XGBoost · Pandas · Streamlit

**Deployment**:
```bash
pip install -r requirements.txt
python train_pipeline.py   # train models first
streamlit run app.py       # launch dashboard
```
    """)
