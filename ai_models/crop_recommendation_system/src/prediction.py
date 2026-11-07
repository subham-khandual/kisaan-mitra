import os
import numpy as np
import pandas as pd
import joblib

class CropPredictor:
    def __init__(self, models_dir):
        """
        Initialize predictor by loading the scaler, label encoder, and best trained model.
        :param models_dir: Directory containing model files.
        """
        self.models_dir = models_dir
        self.scaler_path = os.path.join(models_dir, 'scaler.pkl')
        self.encoder_path = os.path.join(models_dir, 'label_encoder.pkl')
        self.model_path = os.path.join(models_dir, 'best_crop_model.pkl')
        
        self.scaler = None
        self.label_encoder = None
        self.model = None
        
        # Load artifacts immediately
        self.load_artifacts()

    def load_artifacts(self):
        """
        Loads fitted scaler, label encoder, and the best model from files.
        """
        if not os.path.exists(self.scaler_path):
            raise FileNotFoundError(f"Fitted scaler not found at {self.scaler_path}. Please run training first.")
        if not os.path.exists(self.encoder_path):
            raise FileNotFoundError(f"Label encoder not found at {self.encoder_path}. Please run training first.")
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Best model not found at {self.model_path}. Please run training first.")
            
        self.scaler = joblib.load(self.scaler_path)
        self.label_encoder = joblib.load(self.encoder_path)
        self.model = joblib.load(self.model_path)
        print("[+] Prediction artifacts loaded successfully!")

    def predict(self, n, p, k, temperature, humidity, ph, rainfall):
        """
        Predict the best crop for single set of inputs.
        :param n: Nitrogen (mg/kg)
        :param p: Phosphorus (mg/kg)
        :param k: Potassium (mg/kg)
        :param temperature: Temperature (°C)
        :param humidity: Humidity (%)
        :param ph: pH value of soil
        :param rainfall: Rainfall (mm)
        :return: Dict containing 'crop', 'confidence', and 'probabilities'
        """
        # Create a DataFrame with column names matching scaler fitting
        input_data = pd.DataFrame([[n, p, k, temperature, humidity, ph, rainfall]], 
                                  columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
        
        # Scale the inputs
        scaled_input = self.scaler.transform(input_data)
        
        # Predict class
        prediction = self.model.predict(scaled_input)[0]
        crop_recommended = self.label_encoder.inverse_transform([prediction])[0]
        
        # Calculate confidence probability
        confidence = 1.0
        probabilities_dict = {}
        
        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(scaled_input)[0]
            # Get class index for predicted label
            prediction_idx = list(self.model.classes_).index(prediction)
            confidence = probabilities[prediction_idx]
            
            # Map all probabilities to crop labels
            for idx, prob in enumerate(probabilities):
                crop_name = self.label_encoder.inverse_transform([self.model.classes_[idx]])[0]
                probabilities_dict[crop_name] = float(prob)
                
            # Sort class probabilities in descending order
            probabilities_dict = dict(sorted(probabilities_dict.items(), key=lambda item: item[1], reverse=True))
        else:
            probabilities_dict[crop_recommended] = 1.0
            
        return {
            'crop': crop_recommended,
            'confidence': float(confidence),
            'all_probabilities': probabilities_dict
        }

    def predict_dataframe(self, df):
        """
        Predict crops for a batch DataFrame of raw inputs.
        :param df: DataFrame containing features: N, P, K, temperature, humidity, ph, rainfall
        :return: DataFrame with appended predictions and confidence
        """
        # Check columns
        required_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"DataFrame must contain column '{col}'")
                
        # Scale
        scaled_features = self.scaler.transform(df[required_cols])
        
        # Predict
        predictions = self.model.predict(scaled_features)
        recommended_crops = self.label_encoder.inverse_transform(predictions)
        
        output_df = df.copy()
        output_df['Recommended_Crop'] = recommended_crops
        
        # Get confidence if model supports
        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(scaled_features)
            confidences = []
            for i, pred in enumerate(predictions):
                pred_idx = list(self.model.classes_).index(pred)
                confidences.append(probabilities[i][pred_idx])
            output_df['Confidence'] = confidences
        else:
            output_df['Confidence'] = 1.0
            
        return output_df
