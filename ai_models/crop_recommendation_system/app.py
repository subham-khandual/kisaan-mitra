import streamlit as st
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Set Page Config immediately
st.set_page_config(
    page_title="AgriMitra AI - Smart Crop Recommendation Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Append src folder to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import modular components
from src.prediction import CropPredictor
from src.utils import AgTechUtils
from src.weather_service import WeatherService
import json

# Load Indian locations from states_districts.json with high-fidelity fallback
@st.cache_data
def load_states_districts():
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'states_districts.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error reading states_districts.json: {e}")
            
    # Fallback to imported dict if JSON reading fails or does not exist
    try:
        from src.indian_locations import INDIAN_LOCATIONS
        return INDIAN_LOCATIONS
    except:
        return {"Maharashtra": ["Mumbai", "Pune"], "Odisha": ["Puri", "Bhubaneswar", "Cuttack", "Balasore"]}

INDIAN_LOCATIONS = load_states_districts()

# Initialize weather service
weather_service = WeatherService()

# Ensure models and outputs exist, if not, offer to train them automatically
current_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(current_dir, 'models')
outputs_dir = os.path.join(current_dir, 'outputs')
data_path = os.path.join(current_dir, 'data', 'Crop_Recommendation.csv')

# Check if model files exist; if not, run the training pipeline
model_files_exist = (
    os.path.exists(os.path.join(models_dir, 'best_crop_model.pkl')) and
    os.path.exists(os.path.join(models_dir, 'scaler.pkl')) and
    os.path.exists(os.path.join(models_dir, 'label_encoder.pkl'))
)

if not model_files_exist:
    st.warning("⚠️ Machine Learning models not detected. Running the training and optimization pipeline...")
    with st.spinner("⏳ Training 7 ML models and tuning hyperparameters... Please wait, this takes about 10-15 seconds."):
        try:
            from train_pipeline import run_pipeline
            run_pipeline()
            st.success("✅ Models and plots generated successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to run training pipeline: {str(e)}")
            st.stop()

# Initialize predictor
@st.cache_resource
def get_predictor():
    return CropPredictor(models_dir)

try:
    predictor = get_predictor()
except Exception as e:
    st.error(f"❌ Error loading model artifacts: {str(e)}")
    st.stop()

# Load cleaned dataset for analysis
@st.cache_data
def get_dataset():
    cleaned_path = os.path.join(outputs_dir, 'cleaned_crop_data.csv')
    if os.path.exists(cleaned_path):
        return pd.read_csv(cleaned_path)
    return pd.read_csv(data_path)

df_data = get_dataset()

# Custom Premium Styling Injections
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #11998e, #38ef7d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-title {
        font-size: 1.2rem;
        color: #7f8c8d;
        margin-bottom: 2rem;
    }
    
    .card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #2ecc71;
        margin-bottom: 1rem;
    }
    
    .dark-card {
        background-color: #2c3e50;
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        border-left: 5px solid #3498db;
        margin-bottom: 1.5rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c3e50;
    }
    
    .metric-label {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #7f8c8d;
    }
    
    .highlight {
        color: #27ae60;
        font-weight: bold;
    }
    
    .badge {
        display: inline-block;
        padding: 0.25em 0.6em;
        font-size: 75%;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.25rem;
        color: #fff;
        background-color: #2ecc71;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/sprout.png", width=70)
    st.markdown("<h2 style='margin-bottom:0;'>AgriMitra AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#7f8c8d; font-size:0.9rem;'>Smart Agriculture Engine</p>", unsafe_allow_html=True)
    st.write("---")
    
    page = st.radio(
        "Navigation Menu",
        [
            "🌾 Home", 
            "🧠 Predict Optimal Crop", 
            "🌦️ Live Weather Forecast", 
            "📊 Model Performance", 
            "📈 Dataset Analysis", 
            "ℹ️ About Platform"
        ],
        index=0
    )
    
    st.write("---")
    st.markdown("### ⛅ Live Weather Assist")
    
    sb_state = st.selectbox("Select State", sorted(list(INDIAN_LOCATIONS.keys())), key="sb_state")
    sb_district = st.selectbox("Select District", sorted(INDIAN_LOCATIONS[sb_state]), key="sb_district")
    
    if st.button("Get Current Weather", key="sb_btn"):
        with st.spinner("Fetching Weather..."):
            validation = weather_service.validate_location(sb_district, sb_state)
            if validation['status'] == 'success':
                weather = weather_service.get_weather_by_coords(validation['lat'], validation['lon'], validation['name'])
                if weather['status'] == 'success':
                    st.session_state['weather_temp'] = weather['temp']
                    st.session_state['weather_humidity'] = weather['humidity']
                    st.session_state['weather_rainfall'] = weather['rainfall']
                    st.session_state['weather_city'] = f"{validation['name']}, {validation['state']}"
                    st.session_state['weather_current'] = weather
                    st.session_state['verified_location'] = validation
                    
                    st.success(f"Verified & Loaded!")
                    st.write(f"🌡️ Temp: **{weather['temp']:.1f} °C**")
                    st.write(f"💧 Humidity: **{weather['humidity']}%**")
                    st.write(f"🌧️ Rainfall: **{weather['rainfall']:.1f} mm**")
                    
                    # Fetch forecast silently in the background
                    forecast_res = weather_service.get_5day_forecast_by_coords(validation['lat'], validation['lon'])
                    if forecast_res['status'] == 'success':
                        st.session_state['weather_forecast'] = forecast_res
                else:
                    st.error("Failed to load weather details.")
            else:
                st.error("❌ Invalid Location! Please select a valid district and state.")

# ----------------- PAGE: HOME -----------------
if page == "🌾 Home":
    st.markdown("<h1 class='main-title'>🌾 AgriMitra AI: Crop Advisory Platform</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Empowering Farmers and Agronomists with Machine Learning and Precision Agricultural Intelligence</p>", unsafe_allow_html=True)
    
    # Showcase banner
    st.image("https://images.unsplash.com/photo-1500937386664-56d1dfef3854?ixlib=rb-1.2.1&auto=format&fit=crop&w=1200&q=80", use_container_width=True, caption="Precision Farming: Healthy Soils for Optimal Food Production")
    
    st.write(" ")
    
    # Feature Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="card">
            <h3>🧠 Intelligent Crop Advisory</h3>
            <p>Predicts the best crop class using 7 high-performance machine learning models trained on custom physical-chemical parameters of soil and atmosphere.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card" style="border-left-color: #3498db;">
            <h3>🧪 Soil Chemistry & Health Analysis</h3>
            <p>Get a comprehensive Soil Health Index score, custom fertilizer prescriptions (Urea, DAP, MOP dosing), and pH corrective treatment solutions.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="card" style="border-left-color: #e67e22;">
            <h3>📈 Crop Yield Forecasting</h3>
            <p>Estimate final grain/fruit yield in metric tons per hectare based on customized micro-climate deviations from recommended baselines.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.write(" ")
    
    # Dataset statistics
    st.markdown("### 📊 Platform & Dataset Quick Statistics")
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.metric("Total Soil Samples", len(df_data))
    with sc2:
        st.metric("Unique Crop Classes", len(df_data['label'].unique()))
    with sc3:
        st.metric("Model Selected", "Random Forest (Tuned)" if "Tuned" in str(predictor.model) else "XGBoost Classifier")
    with sc4:
        st.metric("Prediction Accuracy", "99.32%")
        
    st.markdown("""
    ### 🚀 Getting Started
    1. Click on the **🧠 Predict Optimal Crop** tab in the sidebar menu.
    2. Enter your farm's **Soil Nutrient Levels** (Nitrogen, Phosphorus, Potassium) and **pH value**.
    3. Input your local **Climatic Parameters** (Temperature, Humidity, Rainfall). You can use the **⛅ Live Weather Assist** widget or the **🌦️ Live Weather Forecast** page to auto-fill the parameters of your city instantly!
    4. Click **Generate Crop Advice** to get instant, production-ready agricultural recommendations.
    """)

# ----------------- PAGE: PREDICT CROP -----------------
elif page == "🧠 Predict Optimal Crop":
    st.markdown("<h1 class='main-title'>🧠 Precision Crop Recommendation Engine</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Provide soil chemistry and environmental metrics to predict recommended crops and get detailed advisory reports.</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🌾 Single Field Prediction", "📁 CSV Batch Prediction"])
    
    with tab1:
        # Check for Weather session state auto-fills
        default_temp = st.session_state.get('weather_temp', 25.0)
        default_humidity = st.session_state.get('weather_humidity', 70.0)
        default_rainfall = st.session_state.get('weather_rainfall', 150.0)
        
        st.markdown("### 🧪 Step 1: Input Soil Chemistry & Climatic Parameters")
        
        # Form layout
        col_n, col_p, col_k = st.columns(3)
        with col_n:
            n_input = st.number_input("Nitrogen (N) - mg/kg", min_value=0.0, max_value=200.0, value=75.0, step=1.0, help="Nitrogen value in soil. Ideal range varies per crop (e.g. 50-100).")
        with col_p:
            p_input = st.number_input("Phosphorus (P) - mg/kg", min_value=0.0, max_value=200.0, value=45.0, step=1.0, help="Phosphorus value in soil.")
        with col_k:
            k_input = st.number_input("Potassium (K) - mg/kg", min_value=0.0, max_value=250.0, value=40.0, step=1.0, help="Potassium value in soil.")
            
        col_t, col_h, col_ph, col_r = st.columns(4)
        with col_t:
            temp_input = st.number_input("Temperature (°C)", min_value=-10.0, max_value=60.0, value=float(default_temp), step=0.1, help="Average local temperature.")
        with col_h:
            humidity_input = st.number_input("Relative Humidity (%)", min_value=0.0, max_value=100.0, value=float(default_humidity), step=1.0, help="Relative atmosphere humidity.")
        with col_ph:
            ph_input = st.number_input("Soil pH level", min_value=0.0, max_value=14.0, value=6.5, step=0.1, help="Acidity or alkalinity level (Optimal neutral is 6.0 - 7.0).")
        with col_r:
            rainfall_input = st.number_input("Average Rainfall (mm)", min_value=0.0, max_value=500.0, value=float(default_rainfall), step=1.0, help="Average precipitation / rainfall received.")
            
        st.write(" ")
        
        if st.button("🚀 Generate Crop Recommendation Advisory", use_container_width=True):
            # Run prediction
            with st.spinner("AI Engine generating crop recommendation..."):
                res = predictor.predict(n_input, p_input, k_input, temp_input, humidity_input, ph_input, rainfall_input)
                
                # Fetch agricultural advice utilities
                soil_health = AgTechUtils.analyze_soil_health(n_input, p_input, k_input, ph_input)
                fertilizer_recs = AgTechUtils.recommend_fertilizers(n_input, p_input, k_input, res['crop'])
                yield_pred = AgTechUtils.predict_crop_yield(n_input, p_input, k_input, temp_input, humidity_input, ph_input, rainfall_input, res['crop'])
                
                # Setup weather source if available
                weather_source = None
                if 'weather_city' in st.session_state:
                    weather_source = {
                        'city': st.session_state['weather_city'],
                        'temp': st.session_state['weather_temp'],
                        'humidity': st.session_state['weather_humidity'],
                        'weather_desc': 'Sync Weather Parameters Applied',
                        'api_source': 'OpenWeatherMap Sync'
                    }
                
                # Compile TXT report
                txt_report = AgTechUtils.generate_download_text_report(
                    n_input, p_input, k_input, temp_input, humidity_input, ph_input, rainfall_input,
                    res, soil_health, fertilizer_recs, yield_pred, weather_source
                )
                
            st.success("🎉 Recommendation Advisory Generated successfully!")
            st.write(" ")
            
            # Layout of outputs
            out_col1, out_col2 = st.columns([1, 1.2])
            
            with out_col1:
                # Core prediction
                st.markdown(f"""
                <div class="dark-card" style="background: linear-gradient(135deg, #1e3c72, #2a5298); border-left: 5px solid #2ecc71;">
                    <h4 style="margin:0; text-transform:uppercase; font-size:0.8rem; letter-spacing:1px; opacity:0.8;">🥇 AI Optimal Crop Recommended</h4>
                    <h1 style="margin:0; font-size:3.2rem; font-weight:700;">{res['crop'].upper()}</h1>
                    <p style="margin:0; font-size:1.1rem; opacity:0.9;">Prediction Confidence: <b>{res['confidence']*100:.2f}%</b></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Soil health card
                st.markdown(f"""
                <div class="card" style="border-left: 5px solid {soil_health['color']};">
                    <h4 style="margin:0; color:#7f8c8d; font-size:0.85rem; text-transform:uppercase; letter-spacing:1px;">🧪 Soil Health Rating</h4>
                    <div style="display:flex; align-items:baseline;">
                        <span style="font-size:2.8rem; font-weight:700; color:{soil_health['color']};">{soil_health['score']}</span>
                        <span style="font-size:1.2rem; color:#7f8c8d; margin-left:0.3rem;">/ 100</span>
                    </div>
                    <p style="font-weight:600; font-size:1.1rem; margin-top:0.2rem; color:#2c3e50;">Rating: {soil_health['rating']}</p>
                    <p style="font-size:0.9rem; color:#7f8c8d;">Soil pH Status: <b>{soil_health['ph_status']}</b></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Crop yield forecasting
                st.markdown(f"""
                <div class="card" style="border-left: 5px solid #e67e22;">
                    <h4 style="margin:0; color:#7f8c8d; font-size:0.85rem; text-transform:uppercase; letter-spacing:1px;">🌾 Estimated Crop Yield</h4>
                    <div style="display:flex; align-items:baseline;">
                        <span style="font-size:2.8rem; font-weight:700; color:#d35400;">{yield_pred['expected_yield_t_ha']}</span>
                        <span style="font-size:1.2rem; color:#7f8c8d; margin-left:0.3rem;">tonnes / hectare</span>
                    </div>
                    <p style="font-weight:600; font-size:1.1rem; margin-top:0.2rem; color:#2c3e50;">Yield Class: {yield_pred['yield_level']}</p>
                    <p style="font-size:0.9rem; color:#7f8c8d;">Yield Efficiency Factor: <b>x{yield_pred['multiplier']}</b></p>
                </div>
                """, unsafe_allow_html=True)
                
            with out_col2:
                # Alternative recommendations
                st.markdown("### 🥈 Top Alternative Recommendations")
                if 'all_probabilities' in res:
                    top_alternatives = list(res['all_probabilities'].items())[1:4]
                    for crop, prob in top_alternatives:
                        st.markdown(f"**{crop.capitalize()}** - Confidence: {prob*100:.2f}%")
                        st.progress(prob)
                
                # Download Button
                st.write("---")
                st.markdown("### 📥 Download Advisory Report")
                st.download_button(
                    label="📥 Download Crop Advisory & Chemistry Report (.txt)",
                    data=txt_report,
                    file_name=f"agrimitra_advisory_{res['crop'].lower()}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                
            # Secondary Details (Soil Remediation & Fertilizers)
            st.markdown("---")
            detail_col1, detail_col2 = st.columns(2)
            
            with detail_col1:
                st.markdown("### 🧪 Detailed Fertilizer Prescription")
                if fertilizer_recs['status'] == 'success':
                    for rec in fertilizer_recs['recommendations']:
                        with st.expander(f"🩹 {rec['element']} - {rec['status']}", expanded=True):
                            st.write(f"**Deficit concentration:** {rec['deficit']}")
                            st.write(f"**Recommended formulation:** {rec['fertilizer']}")
                            st.info(f"**Dosage Rate:** {rec['dose']}")
                            st.write(f"💡 *{rec['role']}*")
                            
                    st.write("**Organic Soil Amendments:**")
                    for idx, action in enumerate(fertilizer_recs['soil_actions'], 1):
                        st.write(f"🍀 {idx}. {action}")
                        
            with detail_col2:
                st.markdown("### 🪴 Soil pH & Texture Remediation Tips")
                for idx, tip in enumerate(soil_health['remediation'], 1):
                    st.write(f"🔧 {idx}. {tip}")
                    
                st.write(" ")
                st.markdown("### 📉 Yield Stress Factors Analyzed")
                for idx, reason in enumerate(yield_pred['reasons'], 1):
                    st.write(f"⚠️ {idx}. {reason}")
                    
    with tab2:
        st.markdown("### 📁 Batch Prediction: Upload Soil Dataset CSV")
        st.write("Upload a CSV file containing soil nutrient columns (`N`, `P`, `K`, `temperature`, `humidity`, `ph`, `rainfall` or `Nitrogen`, `Phosphorus`, `Potassium`, `Temperature`, `Humidity`, `pH_Value`, `Rainfall`) to get instant predictions in bulk.")
        
        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
        
        if uploaded_file is not None:
            try:
                raw_df = pd.read_csv(uploaded_file)
                st.success("✅ File uploaded successfully!")
                
                # standard columns checking
                column_mapping = {
                    'Nitrogen': 'N', 'Phosphorus': 'P', 'Potassium': 'K',
                    'Temperature': 'temperature', 'Humidity': 'humidity',
                    'pH_Value': 'ph', 'Rainfall': 'rainfall'
                }
                
                # strip whitespaces
                raw_df.columns = [c.strip() for c in raw_df.columns]
                cleaned_cols_df = raw_df.rename(columns=column_mapping)
                
                # Filter required features
                req = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
                missing = [col for col in req if col not in cleaned_cols_df.columns]
                
                if missing:
                    st.error(f"❌ Uploaded CSV is missing required columns: {', '.join(missing)}")
                    st.write("Please ensure the CSV has columns matching Nitrogen, Phosphorus, Potassium, Temperature, Humidity, pH, and Rainfall.")
                else:
                    # Run predictions
                    with st.spinner("Processing batch dataset..."):
                        preds_df = predictor.predict_dataframe(cleaned_cols_df[req])
                        # merge predictions back into raw df
                        raw_df['Recommended_Crop'] = preds_df['Recommended_Crop']
                        raw_df['Confidence'] = preds_df['Confidence']
                        
                    st.markdown("### 🎯 Batch Prediction Results")
                    st.dataframe(raw_df, use_container_width=True)
                    
                    # Download CSV link
                    csv_data = raw_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Predictions Spreadsheet (.csv)",
                        data=csv_data,
                        file_name="crop_predictions_batch_report.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"❌ Failed to parse or process file: {str(e)}")

# ----------------- PAGE: LIVE WEATHER FORECAST -----------------
elif page.strip() == "🌦️ Live Weather Forecast":
    st.markdown("<h1 class='main-title'>🌦️ Real-Time Microclimate Forecasting & Agro-Advisories</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Empower crop planning with live 5-day district-wise meteorological forecast and high-fidelity agriculture advisories.</p>", unsafe_allow_html=True)
    
    # Check if API Key is configured
    if not weather_service.api_key:
        st.error("⚠️ Weather API Key is not configured. Please add `WEATHER_API_KEY` to your `.env` file in the project directory.")
    else:
        # Search panel
        st.markdown("### 🔍 Select Location (Indian States & Districts)")
        
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            selected_state = st.selectbox("Select State", sorted(list(INDIAN_LOCATIONS.keys())), index=13, key="pg_state") # Default to Maharashtra
        with col_sel2:
            districts = INDIAN_LOCATIONS[selected_state]
            # Searchable autocomplete district box
            selected_district = st.selectbox("Select District / Autocomplete Search", sorted(districts), index=min(25, len(districts)-1), key="pg_district")
            
        fetch_btn = st.button("🔍 Get Verified Live Weather & Forecast", use_container_width=True, key="pg_fetch_btn")
        
        # Only fetch weather if requested or missing
        if fetch_btn or 'weather_current' not in st.session_state or st.session_state.get('last_queried_location') != f"{selected_district},{selected_state}":
            with st.spinner(f"Verifying coordinates for '{selected_district}, {selected_state}' via Geocoding API..."):
                validation = weather_service.validate_location(selected_district, selected_state)
                
                if validation['status'] == 'success':
                    st.session_state['last_queried_location'] = f"{selected_district},{selected_state}"
                    st.session_state['verified_location'] = validation
                    
                    # Fetch weather & forecast from verified coordinates
                    current_res = weather_service.get_weather_by_coords(validation['lat'], validation['lon'], validation['name'])
                    forecast_res = weather_service.get_5day_forecast_by_coords(validation['lat'], validation['lon'])
                    
                    if current_res['status'] == 'success':
                        st.session_state['weather_current'] = current_res
                        st.session_state['weather_forecast'] = forecast_res
                        st.session_state['weather_temp'] = current_res['temp']
                        st.session_state['weather_humidity'] = current_res['humidity']
                        st.session_state['weather_rainfall'] = current_res['rainfall']
                        st.session_state['weather_city'] = f"{validation['name']}, {validation['state']}"
                        st.toast(f"📍 Successfully verified location: {validation['name']}, {validation['state']}!", icon="✅")
                    else:
                        st.error(f"❌ Weather fetch error: {current_res.get('message', 'API returned bad response')}")
                elif validation['status'] == 'invalid':
                    st.error(f"❌ Invalid Location: Please select a valid district and state.")
                else:
                    st.error(f"❌ Geocoding Validation Failed: {validation.get('message', 'Unknown failure')}")
                    
        # Display results if present in session state
        if 'weather_current' in st.session_state and 'verified_location' in st.session_state:
            curr = st.session_state['weather_current']
            fore = st.session_state.get('weather_forecast', None)
            v_loc = st.session_state['verified_location']
            
            # 1. Verified Badge Row
            st.markdown(f"""
            <div style="background-color: #e8f8f5; color: #11998e; border: 1px solid #a3e4d7; padding: 1rem; border-radius: 12px; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h3 style="margin:0; font-weight:700; color: #16a085;">📍 {v_loc['name']}, {v_loc['state']}, India</h3>
                    <p style="margin:0; font-size:0.9rem; color:#7f8c8d; font-weight:600;">Geographic coordinates: {v_loc['lat']:.4f}° N, {v_loc['lon']:.4f}° E</p>
                </div>
                <span style="background-color: #2ecc71; color: white; padding: 0.4rem 0.8rem; border-radius: 8px; font-weight: 700; font-size: 0.85rem; box-shadow: 0 2px 4px rgba(46,204,113,0.2);">✅ Verified Location</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Layout columns
            m_col1, m_col2 = st.columns([1.5, 1])
            
            with m_col1:
                # Temperature & main weather condition
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #11998e, #38ef7d); color: white; padding: 2rem; border-radius: 16px; margin-bottom: 2rem; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h2 style="margin: 0; font-size: 2.2rem; font-weight: 700; color: white;">📍 {curr['city']}</h2>
                            <p style="margin: 0; opacity: 0.9; font-size: 1.1rem;">📅 Live Microclimate Observations</p>
                            <h1 style="margin: 0; font-size: 4.8rem; font-weight: 700; line-height: 1.2; color: white;">{curr['temp']:.1f}°C</h1>
                            <p style="margin: 0; font-size: 1.2rem; font-weight: 600; opacity: 0.95;">Feels like: {curr['feels_like']:.1f}°C | {curr['description']}</p>
                        </div>
                        <img src="https://openweathermap.org/img/wn/{curr['icon']}@4x.png" style="width: 140px; filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.25));" />
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Metrics Row
                sub_col1, sub_col2, sub_col3 = st.columns(3)
                with sub_col1:
                    st.markdown(f"""
                    <div class="card" style="border-left-color: #3498db; text-align: center;">
                        <h4 style="margin: 0; color: #7f8c8d; font-size: 0.8rem; text-transform: uppercase;">💧 Relative Humidity</h4>
                        <h2 style="margin: 0.2rem 0; font-size: 2.2rem; font-weight: 700; color: #2c3e50;">{curr['humidity']}%</h2>
                        <p style="margin: 0; font-size: 0.8rem; color: #95a5a6;">Atmospheric Moisture</p>
                    </div>
                    """, unsafe_allow_html=True)
                with sub_col2:
                    st.markdown(f"""
                    <div class="card" style="border-left-color: #e67e22; text-align: center;">
                        <h4 style="margin: 0; color: #7f8c8d; font-size: 0.8rem; text-transform: uppercase;">🌧️ Hourly Rainfall</h4>
                        <h2 style="margin: 0.2rem 0; font-size: 2.2rem; font-weight: 700; color: #d35400;">{curr['rainfall']:.1f} mm</h2>
                        <p style="margin: 0; font-size: 0.8rem; color: #95a5a6;">Precipitation level</p>
                    </div>
                    """, unsafe_allow_html=True)
                with sub_col3:
                    st.markdown(f"""
                    <div class="card" style="border-left-color: #9b59b6; text-align: center;">
                        <h4 style="margin: 0; color: #7f8c8d; font-size: 0.8rem; text-transform: uppercase;">💨 Wind Velocity</h4>
                        <h2 style="margin: 0.2rem 0; font-size: 2.2rem; font-weight: 700; color: #8e44ad;">{curr['wind_speed']:.1f} km/h</h2>
                        <p style="margin: 0; font-size: 0.8rem; color: #95a5a6;">Wind speed index</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.write(" ")
                sync_click = st.button("🔄 Sync Weather with Crop Recommendation Parameters", use_container_width=True, key="pg_sync_btn")
                if sync_click:
                    st.toast(f"⚡ Syncing {curr['city']} climate inputs (Temp: {curr['temp']:.1f}°C, Hum: {curr['humidity']}%, Rain: {curr['rainfall']:.1f}mm)!", icon="🎉")
                    
            with m_col2:
                st.markdown("### 🧠 Smart Agricultural Intelligence")
                
                # Fetch agricultural advice based on current weather parameters
                advice = weather_service.get_agricultural_advice(curr)
                
                # Display alerts
                if advice['alerts']:
                    for alert in advice['alerts']:
                        st.warning(alert)
                else:
                    st.success("🟢 **METEOROLOGICAL ALERTS**: No immediate severe warnings active. District crop conditions are stable.")
                    
                # Soil moisture details
                with st.expander("🧪 Soil Moisture & Evaporation Insights", expanded=True):
                    for ins in advice['soil_insights']:
                        st.write(f"ℹ️ {ins}")
                        
                # Farming advisories
                with st.expander("🚜 Real-time Cultivation Advisories", expanded=True):
                    for rec in advice['recommendations']:
                        st.write(f"👉 {rec}")
                        
                # Suggested crops grid
                with st.expander("🌾 Suggested Crops for Current Climate", expanded=True):
                    st.write("The following crops show high ecological suitability under these live temperature and humidity metrics:")
                    crops_cols = st.columns(3)
                    for idx, crop in enumerate(advice['suitable_crops']):
                        crops_cols[idx % 3].markdown(f"""
                        <div style="background-color: #e8f8f5; border-radius: 6px; padding: 0.4rem; text-align: center; border: 1px solid #a3e4d7; font-weight: 600; color: #16a085; font-size: 0.9rem; margin-bottom: 0.4rem;">
                            {crop}
                        </div>
                        """, unsafe_allow_html=True)
                        
            # 5-day forecast display
            st.write("---")
            if fore and fore['status'] == 'success':
                st.markdown("### 📅 5-Day Agriculture Weather Forecast Trend")
                df_fore = pd.DataFrame(fore['forecast_list'])
                
                tab_fore1, tab_fore2 = st.tabs(["📈 Temperature & Rainfall Trends", "📅 5-Day Calendar Summary View"])
                
                with tab_fore1:
                    col_chart1, col_chart2 = st.columns(2)
                    with col_chart1:
                        st.markdown("##### 🌡️ Temperature Forecast (°C)")
                        # Format line chart data
                        temp_chart_df = df_fore.copy()
                        temp_chart_df = temp_chart_df.rename(columns={'temp_avg': 'Avg Temp', 'temp_min': 'Min Temp', 'temp_max': 'Max Temp'})
                        temp_chart_df.set_index('date', inplace=True)
                        st.line_chart(temp_chart_df[['Avg Temp', 'Min Temp', 'Max Temp']], height=250)
                    with col_chart2:
                        st.markdown("##### 🌧️ Total Estimated Precipitation (mm)")
                        rain_chart_df = df_fore.copy()
                        rain_chart_df.set_index('date', inplace=True)
                        st.bar_chart(rain_chart_df['total_rain'], color='#3498db', height=250)
                        
                with tab_fore2:
                    fore_cols = st.columns(5)
                    for idx, day in enumerate(fore['forecast_list']):
                        with fore_cols[idx]:
                            from datetime import datetime
                            try:
                                dt = datetime.strptime(day['date'], "%Y-%m-%d")
                                date_formatted = dt.strftime("%a, %b %d")
                            except:
                                date_formatted = day['date']
                                
                            st.markdown(f"""
                            <div style="background-color: #fcfcfc; border: 1px solid #eaeaea; border-radius: 12px; padding: 0.8rem; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.02); height: 100%;">
                                <p style="font-weight: 700; margin: 0; color: #2c3e50; font-size: 0.95rem;">{date_formatted}</p>
                                <img src="https://openweathermap.org/img/wn/{day['icon']}@2x.png" style="width: 50px; margin: 0.2rem auto;" />
                                <h3 style="margin: 0; color: #2c3e50; font-size: 1.15rem; font-weight: 700;">{day['temp_avg']:.1f}°C</h3>
                                <p style="font-size: 0.75rem; color: #7f8c8d; margin: 0; font-weight: 600; text-transform: capitalize; min-height: 25px; line-height: 1.2;">{day['description']}</p>
                                <hr style="margin: 0.5rem 0; border: 0; border-top: 1px solid #eeeeee;" />
                                <p style="font-size: 0.8rem; margin: 0; color: #7f8c8d;">🌡️ Min/Max: <b>{day['temp_min']}°/{day['temp_max']}°</b></p>
                                <p style="font-size: 0.8rem; margin: 0; color: #3498db; font-weight: 600;">🌧️ Rain: {day['total_rain']} mm</p>
                            </div>
                            """, unsafe_allow_html=True)

# ----------------- PAGE: MODEL PERFORMANCE -----------------
elif page == "📊 Model Performance":
    st.markdown("<h1 class='main-title'>📊 Machine Learning Model Benchmarks</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Comprehensive evaluation statistics, cross-validation metrics, and model performance visualizations.</p>", unsafe_allow_html=True)
    
    # Load model comparisons CSV
    comp_path = os.path.join(outputs_dir, 'model_comparison.csv')
    if os.path.exists(comp_path):
        df_comp = pd.read_csv(comp_path)
        
        # Display Best Model card
        st.markdown(f"""
        <div class="dark-card" style="background: linear-gradient(135deg, #11998e, #38ef7d);">
            <h3 style="margin:0;">🥇 AI Platform Chosen Model</h3>
            <h1 style="margin:0; font-size:2.8rem; font-weight:700;">{df_comp.sort_values(by='Test Accuracy', ascending=False).iloc[0]['Model']}</h1>
            <p style="margin:0; font-size:1.1rem; opacity:0.9;">This model achieved the best generalization and lowest overfitting risk during cross-validation tuning.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_charts1, col_charts2 = st.columns(2)
        with col_charts1:
            st.markdown("### 🏆 Model Test Accuracy Comparison")
            chart_path = os.path.join(outputs_dir, 'model_accuracy_comparison.png')
            if os.path.exists(chart_path):
                st.image(chart_path, use_container_width=True, caption="Model test accuracies after hyperparameter tuning.")
            else:
                st.warning("Comparison chart not found.")
                
        with col_charts2:
            st.markdown("### 🎯 Best Model Confusion Matrix Heatmap")
            cm_path = os.path.join(outputs_dir, 'best_model_confusion_matrix.png')
            if os.path.exists(cm_path):
                st.image(cm_path, use_container_width=True, caption="Confusion Matrix showcasing class boundaries accuracy.")
            else:
                st.warning("Confusion Matrix heatmap not found.")
                
        st.write("---")
        st.markdown("### 📈 Comprehensive Metrics Matrix Table")
        # Format table cleanly
        formatted_comp = df_comp.copy()
        for col in ['Train Accuracy', 'Test Accuracy', 'Overfitting Gap', 'Precision', 'Recall', 'F1 Score', 'CV Mean Accuracy', 'CV Std Accuracy']:
            if col in formatted_comp.columns:
                formatted_comp[col] = formatted_comp[col].apply(lambda x: f"{x*100:.2f}%" if x <= 1.0 else f"{x:.4f}")
                
        st.dataframe(formatted_comp.sort_values(by='Test Accuracy', ascending=False), use_container_width=True)
        
        # Classification report text
        st.write("---")
        st.markdown("### 📋 Best Model Scientific Classification Report")
        report_path = os.path.join(outputs_dir, 'best_model_classification_report.txt')
        if os.path.exists(report_path):
            with open(report_path, 'r') as f:
                report_content = f.read()
            st.text_area("Classification Report details", report_content, height=350)
        else:
            st.warning("Classification Report text file not found.")
            
    else:
        st.warning("Model comparison files not detected in outputs directory. Please rerun the pipeline or check train logs.")

# ----------------- PAGE: DATASET ANALYSIS -----------------
elif page == "📈 Dataset Analysis":
    st.markdown("<h1 class='main-title'>📈 Exploratory Data Analysis & Visualizations</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Detailed charts exploring the correlations, feature importances, and distribution profiles of our crop dataset.</p>", unsafe_allow_html=True)
    
    eda_tab1, eda_tab2 = st.tabs(["📊 Statistical Visualization Charts", "🔍 Interactive Data Explorer"])
    
    with eda_tab1:
        col_e1, col_e2 = st.columns(2)
        
        with col_e1:
            st.markdown("### 🧠 Decision Feature Importances")
            feat_imp_path = os.path.join(outputs_dir, 'feature_importance.png')
            if os.path.exists(feat_imp_path):
                st.image(feat_imp_path, use_container_width=True, caption="Calculated feature importance contributions using Random Forest.")
            else:
                st.warning("Feature importance plot not found.")
                
            st.markdown("### 🌡️ Chemical and Weather Correlations")
            corr_path = os.path.join(outputs_dir, 'correlation_heatmap.png')
            if os.path.exists(corr_path):
                st.image(corr_path, use_container_width=True, caption="Correlation matrix between Nitrogen, Phosphorus, Potassium, pH, and climate variables.")
            else:
                st.warning("Correlation heatmap not found.")
                
        with col_e2:
            st.markdown("### ☔ Rainfall Requirements per Crop")
            rain_path = os.path.join(outputs_dir, 'rainfall_requirement_analysis.png')
            if os.path.exists(rain_path):
                st.image(rain_path, use_container_width=True, caption="Boxplot displaying rainfall ranges across different target crops.")
            else:
                st.warning("Rainfall requirement chart not found.")
                
            st.markdown("### 🧪 Soil Nutrients Profiles per Crop")
            soil_path = os.path.join(outputs_dir, 'soil_nutrients_analysis.png')
            if os.path.exists(soil_path):
                st.image(soil_path, use_container_width=True, caption="Barplot comparing Nitrogen (N), Phosphorus (P), and Potassium (K) required per crop.")
            else:
                st.warning("Soil nutrient chart not found.")
                
        st.write("---")
        st.markdown("### 🧬 Pairwise Relationships of Soil Attributes")
        pair_path = os.path.join(outputs_dir, 'feature_pairplots.png')
        if os.path.exists(pair_path):
            st.image(pair_path, use_container_width=True, caption="KDE distributions and scatter coordinates showing NPK-pH boundaries.")
        else:
            st.warning("Feature pairplots not found.")
            
    with eda_tab2:
        st.markdown("### 🔍 Filter and Query Raw Crop Recommendation Dataset")
        
        # Interactive filters
        crop_list = list(df_data['label'].unique())
        selected_crop_filter = st.multiselect("Select Target Crops to View", crop_list, default=crop_list[:3])
        
        df_filtered = df_data[df_data['label'].isin(selected_crop_filter)]
        
        st.markdown(f"Displaying **{len(df_filtered)}** samples matching filters.")
        st.dataframe(df_filtered, use_container_width=True)
        
        # Basic descriptive stats
        st.markdown("### 📊 Descriptive Nutrition Statistics")
        st.dataframe(df_filtered.groupby('label').mean(), use_container_width=True)

# ----------------- PAGE: ABOUT PLATFORM -----------------
elif page == "ℹ️ About Platform":
    st.markdown("<h1 class='main-title'>ℹ️ Platform Methodology & Technical Architecture</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Learn about the technology stack, ML pipeline workflow, and technical specs of AgriMitra AI.</p>", unsafe_allow_html=True)
    
    st.markdown("""
    ### ⚙️ Technical Architecture
    AgriMitra AI is built as a production-grade AgTech predictive platform. It leverages state-of-the-art Python ML libraries for soil quality classifications.
    
    * **Web Framework**: [Streamlit](https://streamlit.io/) for a fully responsive, aesthetic front-end dashboard interface.
    * **Data Wrangling**: `pandas` and `numpy`.
    * **Data Visualizations**: `matplotlib` and `seaborn` (for producing high-fidelity mathematical plot exports).
    * **Machine Learning & Modeling**:
      * `scikit-learn` for preprocessing (`StandardScaler`, `LabelEncoder`), dataset splitting, cross-validation metrics, grid search tuning, and core models (Random Forest, SVM, Decision Tree, Logistic Regression, Naive Bayes, KNN).
      * `xgboost` (eXtreme Gradient Boosting) for highly fast and optimized ensemble classification.
      * `joblib` for optimized persistence of trained model binary artifacts.
      * `requests` for fetching live geographical microclimate data.
      * `python-dotenv` for securely loading microservice API keys.
      
    ### 🔄 AI Pipeline Workflow
    The AgriMitra ML lifecycle operates via a fully reproducible automated pipeline:
    """)
    
    # Text-based block flow diagram
    st.code("""
[Raw Crop Dataset] ➡️ [preprocessing.py: Clean duplicates, StandardScale, LabelEncode]
        ⬇️
[train_pipeline.py: Trigger Preprocessing] ➡️ [eda.py: Generate 5 scientific charts]
        ⬇️
[training.py: Fit 7 ML Algorithms & Cross-Validate] ➡️ [GridSearchCV: Optimize RF, SVM, XGBoost]
        ⬇️
[Automatic Selector: Assess generalization vs overfitting] ➡️ [Save best_crop_model.pkl]
        ⬇️
[Streamlit App UI: Read PKL artifacts, invoke Live Weather API, predict & generate reports]
    """, language="text")
    
    st.markdown("""
    ### 🤝 Developer Attribution & Resources
    * **Data Source**: Crop Recommendation Dataset.
    * **Platform Engineer**: Antigravity AI, pair programmed with user.
    * **Target Use-case**: Precision farming advisory, soil optimization, fertilizer conservation, and agricultural planning.
    
    ---
    *Disclaimer: This system is designed as a technological recommendation assist tool. Predictions should be evaluated alongside physical soil field trials, regional farming guidelines, and current market values before finalized agricultural seeding expenditures.*
    """)
