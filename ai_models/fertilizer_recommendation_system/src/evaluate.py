"""
evaluate.py - Model Evaluation, Confusion Matrix, Hyperparameter Tuning
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPHS_DIR = os.path.join(BASE_DIR, "outputs", "graphs")


def plot_confusion_matrix(y_test, y_pred, class_names, title="Confusion Matrix"):
    os.makedirs(GRAPHS_DIR, exist_ok=True)
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="YlOrBr",
                xticklabels=class_names, yticklabels=class_names, ax=ax)
    ax.set_xlabel("Predicted", fontsize=12)
    ax.set_ylabel("Actual", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(GRAPHS_DIR, "confusion_matrix.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ Confusion matrix saved → {path}")
    return path


def print_classification_report(y_test, y_pred, class_names):
    report = classification_report(y_test, y_pred, target_names=class_names)
    print("\n📋 Classification Report:")
    print(report)
    return report


def plot_model_comparison(results: dict):
    os.makedirs(GRAPHS_DIR, exist_ok=True)
    names  = list(results.keys())
    accs   = [results[n]["accuracy"] for n in names]
    cv_scores = [results[n]["cv_score"] for n in names]

    x = np.arange(len(names))
    w = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    bars1 = ax.bar(x - w/2, accs,      w, label="Test Accuracy", color="#4CAF50", alpha=0.85)
    bars2 = ax.bar(x + w/2, cv_scores, w, label="CV Score",      color="#FF9800", alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=25, ha="right", fontsize=9)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Score")
    ax.set_title("Model Comparison – Accuracy vs CV Score", fontsize=13, fontweight="bold")
    ax.legend()

    for bar in bars1 + bars2:
        ax.annotate(f"{bar.get_height():.2f}",
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    path = os.path.join(GRAPHS_DIR, "model_comparison.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ Model comparison chart saved → {path}")
    return path


def hyperparameter_tuning(X_train, y_train):
    """Run GridSearch on RF and RandomizedSearch on XGBoost."""
    print("\n🔧 Hyperparameter Tuning (RandomForest)…")
    rf_params = {
        "n_estimators": [50, 100, 200],
        "max_depth":    [None, 5, 10, 20],
        "min_samples_split": [2, 5],
    }
    rf_gs = GridSearchCV(RandomForestClassifier(random_state=42),
                         rf_params, cv=5, scoring="accuracy", n_jobs=-1)
    rf_gs.fit(X_train, y_train)
    print(f"   Best RF params : {rf_gs.best_params_}")
    print(f"   Best RF accuracy: {rf_gs.best_score_:.4f}")

    print("\n🔧 Hyperparameter Tuning (XGBoost)…")
    xgb_params = {
        "n_estimators": [50, 100, 200],
        "max_depth":    [3, 5, 7],
        "learning_rate": [0.01, 0.1, 0.3],
        "subsample":    [0.7, 1.0],
    }
    xgb_rs = RandomizedSearchCV(
        XGBClassifier(use_label_encoder=False, eval_metric="mlogloss",
                      random_state=42, verbosity=0),
        xgb_params, n_iter=10, cv=5, scoring="accuracy",
        random_state=42, n_jobs=-1)
    xgb_rs.fit(X_train, y_train)
    print(f"   Best XGB params : {xgb_rs.best_params_}")
    print(f"   Best XGB accuracy: {xgb_rs.best_score_:.4f}")

    return rf_gs.best_estimator_, xgb_rs.best_estimator_
