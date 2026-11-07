import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

def train_model():
    print("Loading data...")
    df = pd.read_csv('crop_yield.csv')
    # Train on 60,000 diverse samples for high accuracy and fast training
    sample_size = min(60000, len(df))
    df = df.sample(sample_size, random_state=42)
    print(f"Dataset sampled to {sample_size:,} rows.")
    
    # Define categorical and numerical features
    categorical_features = ['Region', 'Soil_Type', 'Crop', 'Weather_Condition']
    boolean_features = ['Fertilizer_Used', 'Irrigation_Used']
    numerical_features = ['Rainfall_mm', 'Temperature_Celsius', 'Days_to_Harvest']
    
    # Convert booleans to int (0/1)
    df[boolean_features] = df[boolean_features].astype(int)
    numerical_features.extend(boolean_features)
    
    X = df.drop('Yield_tons_per_hectare', axis=1)
    y = df['Yield_tons_per_hectare']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create preprocessing steps
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    # Append regressor to preprocessing pipeline
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=50, max_depth=15, random_state=42, n_jobs=-1))
    ])
                               
    print("Training model...")
    pipeline.fit(X_train, y_train)
    
    print("Evaluating model...")
    y_pred = pipeline.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Test RMSE: {rmse:.4f}")
    print(f"Test R2 Score: {r2:.4f}")
    
    # Save the model
    model_path = os.path.join('backend', 'app', 'ml', 'models', 'crop_yield_model.pkl')
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(pipeline, model_path)
    print(f"Model saved to {model_path}")
    
    # Save label encoders mappings or unique values for the frontend
    unique_values = {
        'Region': df['Region'].unique().tolist(),
        'Soil_Type': df['Soil_Type'].unique().tolist(),
        'Crop': df['Crop'].unique().tolist(),
        'Weather_Condition': df['Weather_Condition'].unique().tolist()
    }
    
    import json
    with open(os.path.join('backend', 'app', 'ml', 'models', 'crop_yield_metadata.json'), 'w') as f:
        json.dump(unique_values, f)
    print("Metadata saved.")

if __name__ == "__main__":
    train_model()
