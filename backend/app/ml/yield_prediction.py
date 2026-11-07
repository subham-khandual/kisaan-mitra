import os
import joblib
import pandas as pd

class CropYieldPredictor:
    def __init__(self, models_dir: str):
        self.model_path = os.path.join(models_dir, 'crop_yield_model.pkl')
        self.model = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            print("Crop Yield model loaded successfully.")
        else:
            print(f"Warning: Crop Yield model not found at {self.model_path}.")

    def predict(self, region: str, soil_type: str, crop: str, rainfall_mm: float, 
                temperature_celsius: float, fertilizer_used: bool, 
                irrigation_used: bool, weather_condition: str, days_to_harvest: int):
        if self.model is None:
            raise Exception("Crop Yield model is not loaded.")
        
        # Create a dataframe for the input
        input_data = pd.DataFrame([{
            'Region': region,
            'Soil_Type': soil_type,
            'Crop': crop,
            'Rainfall_mm': rainfall_mm,
            'Temperature_Celsius': temperature_celsius,
            'Fertilizer_Used': int(fertilizer_used),
            'Irrigation_Used': int(irrigation_used),
            'Weather_Condition': weather_condition,
            'Days_to_Harvest': days_to_harvest
        }])
        
        # Predict yield
        prediction = self.model.predict(input_data)[0]
        
        return {
            "estimated_yield_tons_per_hectare": round(prediction, 2)
        }
