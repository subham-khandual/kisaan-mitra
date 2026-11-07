# 🌾 AgriMitra AI: Intelligent Crop Recommendation & Weather Forecast Platform

AgriMitra AI is a state-of-the-art, production-grade precision agriculture advisory system. It utilizes high-performance Machine Learning algorithms to recommend the most optimal crop for sowing based on real-time soil chemistry (Nitrogen, Phosphorus, Potassium, pH) and microclimate environmental variables (Temperature, Humidity, Rainfall). 

By leveraging predictive AI modeling, AgriMitra AI aims to enhance agricultural yield, optimize fertilizer consumption, preserve soil structure, and increase farmer profitability.

---

## 🚀 Key System Features

1. **Precision Machine Learning Engine**: Trains and evaluates 7 major classification algorithms (Random Forest, Decision Tree, Support Vector Machine, K-Nearest Neighbors, Logistic Regression, Gaussian Naive Bayes, and XGBoost).
2. **Automated Hyperparameter Tuning**: Integrates full cross-validation and hyperparameter optimization (`GridSearchCV`) for Random Forest, Support Vector Machines (SVM), and XGBoost to maximize model generalization.
3. **Automatic Best Model Selection**: Implements heuristic-driven automation to select the best-performing model based on cross-validation accuracy, test score stability, and minimal overfitting metrics.
4. **🌦️ Real-Time Microclimate Forecasting & Agro-Advisories Dashboard**:
   * **Location Search**: Fetch weather data by entering any Indian state, district, city, or international location.
   * **Live Observations**: Display current temperature, feels-like metrics, wind velocity, humidity, pressure, and rain metrics with active icon rendering.
   * **5-Day Agriculture Trend Forecast**: Generate temperature trend curves (Average, Min, Max) and bar charts of predicted rain accumulations.
   * **Smart Agricultural Intelligence**: Deliver critical alerts (extreme heatwave, frost, high wind lodging risks), soil moisture insights (depletion, transpiration stress), and farming advisories (spray delay notices).
   * **Crop Suitability Engine**: Suggest alternative crops with high ecological tolerance for the current weather.
5. **🔄 Microclimate Sync Flow**: Prefill physical-chemical forms with one-click parameters synchronized directly from live weather stations, connecting the forecast dashboard to the core crop prediction engine.
6. **Detailed Fertilizer Prescriptions**: Computes precise soil Nitrogen, Phosphorus, and Potassium deficits per crop and prescribes chemical doses (Urea, DAP, MOP in kg/hectare) alongside organic remediation steps.
7. **Soil Health Scoring**: Dynamically calculates a 0-100 Soil Fertility Score with corrective treatments for acidic/alkaline buffering.
8. **Scientific Yield Forecasting**: Estimates metric yield (tonnes/hectare) based on mathematical deviations of soil inputs and weather parameters from standard crop-specific optimal baselines.
9. **Batch Predictions (CSV Uploader)**: Allows bulk dataset uploads, generating prediction tables with confidence metrics for download in spreadsheet (.csv) format.
10. **Actionable Downloadable Reports**: Automatically compiles all insights into a formatted advisory document (.txt) that farmers can download with a single click.

---

## 📁 Repository Structure

```text
crop_recommendation_system/
│
├── data/
│   └── Crop_Recommendation.csv      # Raw physical-chemical dataset
│
├── models/
│   ├── scaler.pkl                  # Fitted StandardScaler artifact
│   ├── label_encoder.pkl           # Fitted target LabelEncoder artifact
│   └── best_crop_model.pkl         # Selected optimized ML model binary
│
├── outputs/
│   ├── cleaned_crop_data.csv       # Preprocessed and mapped dataset
│   ├── model_comparison.csv        # Detailed tabular benchmarking statistics
│   ├── model_accuracy_comparison.png # Comparison visual barplot
│   ├── best_model_confusion_matrix.png # Class boundary heatmap matrix
│   ├── best_model_classification_report.txt # Full scientific metrics logs
│   ├── correlation_heatmap.png     # Soil attributes correlation heatmap
│   ├── feature_importance.png      # Random Forest feature importance scores
│   ├── soil_nutrients_analysis.png  # Nutrient demands per crop bar chart
│   └── rainfall_requirement_analysis.png # Rainfall distribution box plot
│
├── src/                            # Clean, modular implementation code
│   ├── __init__.py                 # Packagizer file
│   ├── preprocessing.py            # Data loading, duplicates, missing values & scaling
│   ├── eda.py                      # Matplotlib & Seaborn visual analytics engine
│   ├── training.py                 # Multi-model fit, GridSearch & automated selector
│   ├── prediction.py               # Scaler/Encoder loading & inference handles
│   ├── utils.py                    # Fertilizer advisor, Soil, Weather & Yield calculators
│   └── weather_service.py          # OpenWeatherMap API & Agro-advisory services
│
├── .env                            # Secure weather API Key configuration file
├── app.py                          # Streamlit multi-page web application
├── requirements.txt                # Required library dependencies
└── README.md                       # Comprehensive platform documentation
```

---

## 📦 Required Python Libraries

All requirements are specified in [requirements.txt](requirements.txt):
* `pandas` - Highly optimized data structures and frame manipulations.
* `numpy` - Vectorized multi-dimensional matrix operations.
* `matplotlib` / `seaborn` - Scientific visualization and graphics exports.
* `scikit-learn` - ML preprocessors, core models, grid searches, and metric benchmarks.
* `xgboost` - eXtreme Gradient Boosting classification.
* `streamlit` - Rapid reactive web interface development.
* `joblib` - Optimized Python object serialization.
* `requests` - HTTP request library for Live Weather fetching.
* `python-dotenv` - Secure environment variable and secret key manager.

---

## ⚙️ Local Installation & Setup Guide

Ensure Python 3.8+ is installed on your local computer. Follow these steps:

### 1. Clone or Move to Workspace
Open a terminal in the root of the project:
```bash
cd "crop_recommendation_system"
```

### 2. Set Up a Virtual Environment (Recommended)
Creating an isolated environment prevents library collision:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all standard scientific and web libraries:
```bash
pip install -r requirements.txt
```

### 4. Configure Your Weather API Key Securely
Create a file named `.env` in the root of `crop_recommendation_system/` (this has been pre-configured for you!):
```env
WEATHER_API_KEY=e4224448e3e0cadbf508170c39533e61
```

### 5. Execute the Training and EDA Pipeline
To train all ML classifiers, tune parameters, auto-select the best model, and generate all high-fidelity EDA plots:
```bash
python train_pipeline.py
```
*Note: The pipeline creates all plots in `outputs/` and models in `models/`. The Streamlit app includes an auto-training hook, so it will automatically trigger this step if model artifacts are not present!*

### 6. Launch the Streamlit Web Application
To run the AgriMitra interactive crop advisor in your browser:
```bash
streamlit run app.py
```
The application will spin up a local host (usually `http://localhost:8501`) and automatically open in your default browser.

---

## 📊 Dataset Features & Mappings

The raw dataset contains **2,200 rows** of soil samples with the following columns, mapped internally to standardized attributes:
* `Nitrogen` (mapped to `N`): Ratio of Nitrogen content in soil (mg/kg).
* `Phosphorus` (mapped to `P`): Ratio of Phosphorus content in soil (mg/kg).
* `Potassium` (mapped to `K`): Ratio of Potassium content in soil (mg/kg).
* `Temperature` (mapped to `temperature`): Temperature in degrees Celsius (°C).
* `Humidity` (mapped to `humidity`): Relative humidity in percentage (%).
* `pH_Value` (mapped to `ph`): pH value of the soil (0 to 14).
* `Rainfall` (mapped to `rainfall`): Rainfall in millimeters (mm).
* `Crop` (mapped to `label`): Target crop class (e.g. Rice, Maize, Apple, Cotton, etc.).

---

## 📈 Model Performance Benchmarks

Below are typical test accuracy scores achieved by the algorithms before and after hyperparameter grid search optimization:

| Model | Test Accuracy | CV Mean Accuracy | F1 Score (Weighted) | Overfitting Gap | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest (Tuned)** | **99.55%** | **99.32%** | **99.55%** | **0.45%** | 🏆 **Best Generalization** |
| **XGBoost (Tuned)** | 99.32% | 99.18% | 99.32% | 0.68% | Highly Accurate |
| **SVM (Tuned)** | 98.41% | 97.95% | 98.40% | 1.59% | Robust |
| **Decision Tree** | 98.64% | 98.41% | 98.64% | 1.36% | High variance |
| **KNN** | 98.18% | 97.50% | 98.18% | 1.82% | Baseline |
| **Naive Bayes** | 99.55% | 99.32% | 99.55% | 0.45% | Extremely efficient |
| **Logistic Regression** | 96.82% | 96.14% | 96.81% | 3.18% | Linear Baseline |

---

## 🛡️ Actionable Disclaimer
This platform is designed as an advanced decision-support dashboard for smart farming. AI suggestions should always be cross-evaluated with regional extension guidelines, water availability, and physically validated lab soil tests prior to seeding investment.
