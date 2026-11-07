"""
utils.py - EDA Graphs and Soil Health Analysis
"""

import os
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPHS_DIR = os.path.join(BASE_DIR, "outputs", "graphs")


def _save(fig, name: str) -> str:
    os.makedirs(GRAPHS_DIR, exist_ok=True)
    path = os.path.join(GRAPHS_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Saved → {path}")
    return path


def plot_fertilizer_distribution(df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(10, 5))
    counts = df["Fertilizer Name"].value_counts()
    bars = ax.bar(counts.index, counts.values,
                  color=sns.color_palette("viridis", len(counts)))
    ax.set_title("Fertilizer Distribution", fontsize=14, fontweight="bold")
    ax.set_xlabel("Fertilizer"); ax.set_ylabel("Count")
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                str(int(bar.get_height())), ha="center", fontsize=9)
    plt.xticks(rotation=20, ha="right")
    return _save(fig, "fertilizer_distribution.png")


def plot_correlation_heatmap(df: pd.DataFrame) -> str:
    num_df = df.select_dtypes(include=[np.number])
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(num_df.corr(), annot=True, fmt=".2f",
                cmap="YlGn", linewidths=0.5, ax=ax)
    ax.set_title("Feature Correlation Heatmap", fontsize=14, fontweight="bold")
    return _save(fig, "correlation_heatmap.png")


def plot_soil_nutrient_analysis(df: pd.DataFrame) -> str:
    nutrients = ["Nitrogen", "Potassium", "Phosphorous"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    palette = ["#4CAF50", "#FF9800", "#2196F3"]
    for ax, nutrient, color in zip(axes, nutrients, palette):
        sns.boxplot(x="Soil Type", y=nutrient, data=df, ax=ax, color=color)
        ax.set_title(f"{nutrient} by Soil Type", fontsize=11, fontweight="bold")
        ax.set_xlabel(""); ax.tick_params(axis="x", rotation=30)
    plt.suptitle("Soil Nutrient Analysis", fontsize=14, fontweight="bold", y=1.02)
    return _save(fig, "soil_nutrient_analysis.png")


def plot_crop_vs_fertilizer(df: pd.DataFrame) -> str:
    pivot = pd.crosstab(df["Crop Type"], df["Fertilizer Name"])
    fig, ax = plt.subplots(figsize=(13, 6))
    pivot.plot(kind="bar", stacked=True, ax=ax,
               colormap="tab10", edgecolor="white", linewidth=0.5)
    ax.set_title("Crop Type vs Fertilizer", fontsize=14, fontweight="bold")
    ax.set_xlabel("Crop Type"); ax.set_ylabel("Count")
    ax.legend(title="Fertilizer", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)
    plt.xticks(rotation=30, ha="right")
    return _save(fig, "crop_vs_fertilizer.png")


def plot_feature_importance(model, feature_names: list) -> str:
    if not hasattr(model, "feature_importances_"):
        print("⚠️  Model has no feature_importances_; skipping plot.")
        return None
    importances = model.feature_importances_
    idx = np.argsort(importances)[::-1]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(len(importances)), importances[idx],
           color=sns.color_palette("YlOrRd", len(importances)))
    ax.set_xticks(range(len(importances)))
    ax.set_xticklabels([feature_names[i] for i in idx], rotation=25, ha="right")
    ax.set_title("Feature Importance", fontsize=14, fontweight="bold")
    ax.set_ylabel("Importance Score")
    return _save(fig, "feature_importance.png")


def plot_temperature_moisture(df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(9, 6))
    scatter = ax.scatter(df["Temperature"], df["Moisture"],
                         c=df["Fertilizer Name"].astype("category").cat.codes,
                         cmap="tab10", alpha=0.75, s=80, edgecolors="white", linewidth=0.5)
    legend = ax.legend(*scatter.legend_elements(),
                       title="Fertilizer", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)
    ax.set_xlabel("Temperature (°C)"); ax.set_ylabel("Moisture (%)")
    ax.set_title("Temperature vs Moisture (by Fertilizer)", fontsize=13, fontweight="bold")
    return _save(fig, "temp_moisture_scatter.png")


def run_full_eda(df: pd.DataFrame, model=None, feature_names=None):
    """Generate all EDA graphs."""
    print("\n📊 Running EDA …")
    plot_fertilizer_distribution(df)
    plot_correlation_heatmap(df)
    plot_soil_nutrient_analysis(df)
    plot_crop_vs_fertilizer(df)
    plot_temperature_moisture(df)
    if model and feature_names:
        plot_feature_importance(model, feature_names)
    print("✅ All EDA graphs saved to outputs/graphs/")
