import os
import sys

# Add src folder to system path so we can import modules cleanly
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.preprocessing import DataPreprocessor
from src.eda import EDAVisualizer
from src.training import ModelTrainer

def run_pipeline():
    print("="*60)
    print("[*] STARTING CROP RECOMMENDATION MODEL TRAINING PIPELINE")
    print("="*60)
    
    # 1. Define paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, 'data', 'Crop_Recommendation.csv')
    models_dir = os.path.join(current_dir, 'models')
    outputs_dir = os.path.join(current_dir, 'outputs')
    
    # Ensure outputs directory exists
    os.makedirs(outputs_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    
    # 2. Preprocess Data
    preprocessor = DataPreprocessor(data_path, models_dir)
    X_train, X_test, y_train, y_test, df_cleaned = preprocessor.preprocess()
    
    # Save a copy of cleaned dataframe for dataset analysis tab in dashboard
    cleaned_df_path = os.path.join(outputs_dir, 'cleaned_crop_data.csv')
    df_cleaned.to_csv(cleaned_df_path, index=False)
    print(f"[+] Cleaned dataset saved to {cleaned_df_path}")
    
    # 3. Perform Exploratory Data Analysis (EDA) & generate charts
    visualizer = EDAVisualizer(outputs_dir)
    visualizer.generate_all_plots(df_cleaned)
    
    # 4. Train Models & Perform Hyperparameter Tuning
    trainer = ModelTrainer(models_dir, outputs_dir)
    
    # Train all base models
    trainer.train_and_evaluate_all(X_train, X_test, y_train, y_test)
    
    # Tune hyper-parameters
    trainer.tune_hyperparameters(X_train, y_train)
    
    # Evaluate newly tuned models
    trainer.evaluate_tuned_on_test(X_train, X_test, y_train, y_test)
    
    # 5. Automatically Select Best Model and Save It
    best_model_name, best_metrics = trainer.select_and_save_best_model(
        X_train, X_test, y_train, y_test, preprocessor.label_encoder
    )
    
    print("\n" + "="*60)
    print("[SUCCESS] MODEL TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"[BEST MODEL] Selected Best Model: {best_model_name}")
    print(f"[ACCURACY]   Test Set Accuracy:  {best_metrics['Test Accuracy']*100:.2f}%")
    print(f"[METRICS]    Outputs saved in:    {outputs_dir}")
    print(f"[SAVE]       Models saved in:     {models_dir}")
    print("="*60)

if __name__ == "__main__":
    run_pipeline()
