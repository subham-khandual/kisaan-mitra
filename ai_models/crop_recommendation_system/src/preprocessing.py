import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib

class DataPreprocessor:
    def __init__(self, data_path, models_dir):
        """
        Initialize preprocessor.
        :param data_path: Path to the raw CSV dataset.
        :param models_dir: Directory to save scaler and label encoder.
        """
        self.data_path = data_path
        self.models_dir = models_dir
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Ensure models directory exists
        os.makedirs(self.models_dir, exist_ok=True)
        
    def load_data(self):
        """
        Load CSV data and standardizes column names.
        """
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Dataset not found at {self.data_path}")
            
        print(f"[*] Loading dataset from {self.data_path}...")
        df = pd.read_csv(self.data_path)
        
        # Display raw columns and shape
        print(f"[*] Loaded dataset shape: {df.shape}")
        
        # Clean column names and map to standard names
        # Map: Nitrogen -> N, Phosphorus -> P, Potassium -> K, pH_Value -> ph, Crop -> label
        column_mapping = {
            'Nitrogen': 'N',
            'Phosphorus': 'P',
            'Potassium': 'K',
            'Temperature': 'temperature',
            'Humidity': 'humidity',
            'pH_Value': 'ph',
            'Rainfall': 'rainfall',
            'Crop': 'label',
            'N': 'N',
            'P': 'P',
            'K': 'K',
            'temperature': 'temperature',
            'humidity': 'humidity',
            'ph': 'ph',
            'rainfall': 'rainfall',
            'label': 'label'
        }
        
        # Strip whitespaces from column names first
        df.columns = [c.strip() for c in df.columns]
        
        # Rename columns using the mapping
        df = df.rename(columns=column_mapping)
        
        # Verify all required columns exist
        required_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label']
        for col in required_cols:
            if col not in df.columns:
                # If there's an exact mismatch, check if there's any similar column
                found = False
                for existing_col in df.columns:
                    if col.lower() in existing_col.lower():
                        df = df.rename(columns={existing_col: col})
                        found = True
                        break
                if not found:
                    raise ValueError(f"Required column '{col}' could not be matched in dataset.")
        
        # Reorder to keep it clean
        df = df[required_cols]
        return df

    def preprocess(self):
        """
        Perform complete data preprocessing: load, clean, scale, split, and save parameters.
        :return: (X_train, X_test, y_train, y_test, df_cleaned)
        """
        # 1. Load data
        df = self.load_data()
        
        # 2. Handle missing values (if any)
        missing_count = df.isnull().sum().sum()
        if missing_count > 0:
            print(f"[!] Found {missing_count} missing values. Filling with median/mode values...")
            for col in ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']:
                df[col] = df[col].fillna(df[col].median())
            df['label'] = df['label'].fillna(df['label'].mode()[0])
        else:
            print("[*] No missing values found in the dataset.")
            
        # 3. Remove duplicates
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            print(f"[!] Found {duplicate_count} duplicates. Removing them...")
            df = df.drop_duplicates().reset_index(drop=True)
            print(f"[*] Shape after duplicate removal: {df.shape}")
        else:
            print("[*] No duplicate rows found in the dataset.")
            
        # 4. Separate features and target
        X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
        y = df['label']
        
        # 5. Encode target labels
        print("[*] Encoding crop labels...")
        y_encoded = self.label_encoder.fit_transform(y)
        
        # 6. Apply StandardScaler
        print("[*] Applying StandardScaler on features...")
        X_scaled = self.scaler.fit_transform(X)
        X_scaled_df = pd.DataFrame(X_scaled, columns=X.columns)
        
        # 7. Split dataset into train/test sets (80/20)
        print("[*] Splitting dataset into train/test sets (80/20)...")
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled_df, y_encoded, test_size=0.20, random_state=42, stratify=y_encoded
        )
        
        # 8. Save scaler and encoder files
        scaler_path = os.path.join(self.models_dir, 'scaler.pkl')
        encoder_path = os.path.join(self.models_dir, 'label_encoder.pkl')
        
        joblib.dump(self.scaler, scaler_path)
        joblib.dump(self.label_encoder, encoder_path)
        
        print(f"[+] StandardScaler saved successfully to {scaler_path}")
        print(f"[+] LabelEncoder saved successfully to {encoder_path}")
        print(f"[*] Training features shape: {X_train.shape}, Test features shape: {X_test.shape}")
        
        return X_train, X_test, y_train, y_test, df
