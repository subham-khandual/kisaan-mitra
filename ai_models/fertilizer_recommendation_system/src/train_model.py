"""
train_model.py - Multi-Model Training & Best Model Selection
Trains 7 ML algorithms, compares them, saves the best model
"""

import os
import joblib
import numpy as np
import warnings
warnings.filterwarnings("ignore")

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from xgboost import XGBClassifier

from preprocess import get_prepared_data

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")


def get_models():
    return {
        "Random Forest":     RandomForestClassifier(n_estimators=100, random_state=42),
        "Decision Tree":     DecisionTreeClassifier(random_state=42),
        "XGBoost":           XGBClassifier(use_label_encoder=False, eval_metric="mlogloss",
                                           random_state=42, verbosity=0),
        "SVM":               SVC(probability=True, random_state=42),
        "KNN":               KNeighborsClassifier(n_neighbors=5),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Naive Bayes":       GaussianNB(),
    }


def train_and_evaluate(X_train, X_test, y_train, y_test):
    """Train all models, compute metrics, return results dict."""
    models  = get_models()
    results = {}

    print("\n" + "="*60)
    print("   FERTILIZER MODEL TRAINING RESULTS")
    print("="*60)

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc  = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec  = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1   = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        cv   = cross_val_score(model, X_train, y_train, cv=5, scoring="accuracy").mean()

        results[name] = {
            "model":     model,
            "accuracy":  acc,
            "precision": prec,
            "recall":    rec,
            "f1":        f1,
            "cv_score":  cv,
        }

        print(f"\n📊 {name}")
        print(f"   Accuracy : {acc:.4f} | CV : {cv:.4f}")
        print(f"   Precision: {prec:.4f} | Recall: {rec:.4f} | F1: {f1:.4f}")

    return results


def select_best(results: dict):
    """Return name and model with highest accuracy."""
    best_name = max(results, key=lambda k: results[k]["accuracy"])
    print(f"\n🏆 Best Model: {best_name} (Accuracy: {results[best_name]['accuracy']:.4f})")
    return best_name, results[best_name]["model"]


def save_best(name, model):
    os.makedirs(MODELS_DIR, exist_ok=True)
    path = os.path.join(MODELS_DIR, "best_fertilizer_model.pkl")
    joblib.dump({"name": name, "model": model}, path)
    print(f"✅ Best model saved → {path}")


def run_training():
    X_train, X_test, y_train, y_test, le_target = get_prepared_data()
    results = train_and_evaluate(X_train, X_test, y_train, y_test)
    best_name, best_model = select_best(results)
    save_best(best_name, best_model)
    return results, best_name, best_model, X_test, y_test, le_target


if __name__ == "__main__":
    run_training()
