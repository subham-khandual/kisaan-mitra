"""
train_pipeline.py - One-click full training pipeline
Run this file to train the model end-to-end
"""

import os
import sys
import io
import pandas as pd
import warnings

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR  = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)

from preprocess import load_data, clean_data
from train_model import run_training
from evaluate import (plot_confusion_matrix, print_classification_report,
                      plot_model_comparison, hyperparameter_tuning)
from utils import run_full_eda
from sklearn.metrics import accuracy_score

FEATURE_NAMES = ["Temperature", "Humidity", "Moisture",
                 "Nitrogen", "Potassium", "Phosphorous",
                 "Soil Type", "Crop Type"]


def main():
    print("=" * 60)
    print("  🌾 FERTILIZER RECOMMENDATION SYSTEM - TRAINING PIPELINE")
    print("=" * 60)

    # ── Step 1: EDA ───────────────────────────────────────────────
    df = load_data()
    df = clean_data(df)
    run_full_eda(df)

    # ── Step 2: Train All Models ──────────────────────────────────
    results, best_name, best_model, X_test, y_test, le_target = run_training()

    # ── Step 3: Evaluation ────────────────────────────────────────
    y_pred      = best_model.predict(X_test)
    class_names = list(le_target.classes_)

    plot_confusion_matrix(y_test, y_pred, class_names,
                          title=f"Confusion Matrix – {best_name}")
    print_classification_report(y_test, y_pred, class_names)
    plot_model_comparison(results)

    # ── Step 4: Feature Importance ────────────────────────────────
    from utils import plot_feature_importance
    plot_feature_importance(best_model, FEATURE_NAMES)

    # ── Step 5: Hyperparameter Tuning ─────────────────────────────
    from preprocess import get_prepared_data
    X_train, X_test2, y_train, y_test2, _ = get_prepared_data()
    hyperparameter_tuning(X_train, y_train)

    print("\n" + "=" * 60)
    print(f"  ✅ TRAINING COMPLETE")
    print(f"  🏆 Best Model : {best_name}")
    print(f"  📊 Accuracy   : {accuracy_score(y_test, y_pred):.4f}")
    print(f"  📁 Models saved in: {os.path.join(BASE_DIR, 'models')}/")
    print(f"  📊 Graphs saved in: {os.path.join(BASE_DIR, 'outputs/graphs')}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
