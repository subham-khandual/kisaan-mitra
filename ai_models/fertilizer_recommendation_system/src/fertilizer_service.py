"""
fertilizer_service.py - Reusable service consumed by backend API and Streamlit
"""

import os
import sys

# Ensure src/ is on PYTHONPATH when called from anywhere
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from predict import predict_fertilizer, get_soil_types, get_crop_types, FERTILIZER_INFO

__all__ = [
    "predict_fertilizer",
    "get_soil_types",
    "get_crop_types",
    "FERTILIZER_INFO",
    "soil_health_check",
    "get_organic_suggestions",
    "get_overuse_warnings",
]


def soil_health_check(nitrogen: float, potassium: float, phosphorous: float) -> dict:
    """Simple rule-based soil health analysis."""
    issues = []
    suggestions = []

    if nitrogen < 10:
        issues.append("⚠️ Low Nitrogen – Growth will be stunted")
        suggestions.append("Apply Urea or organic compost to boost Nitrogen.")
    elif nitrogen > 40:
        issues.append("🔴 Excess Nitrogen – Risk of leaf burn and water contamination")
        suggestions.append("Reduce nitrogen application; use slow-release fertilizers.")

    if potassium < 5:
        issues.append("⚠️ Low Potassium – Weak root system, disease-prone")
        suggestions.append("Apply MOP (Muriate of Potash) or wood ash.")
    elif potassium > 20:
        issues.append("🔴 Excess Potassium – May block calcium and magnesium uptake")

    if phosphorous < 5:
        issues.append("⚠️ Low Phosphorous – Poor root and flower development")
        suggestions.append("Apply DAP or bone meal to improve phosphorous.")
    elif phosphorous > 40:
        issues.append("🔴 Excess Phosphorous – May lead to zinc and iron deficiency")

    health_score = max(0, 100 - len(issues) * 20)
    label = ("🟢 Healthy" if health_score >= 80
             else "🟡 Moderate" if health_score >= 50
             else "🔴 Poor")

    return {
        "score":       health_score,
        "label":       label,
        "issues":      issues,
        "suggestions": suggestions,
    }


def get_organic_suggestions(fertilizer: str) -> list[str]:
    info = FERTILIZER_INFO.get(fertilizer, {})
    alt  = info.get("organic_alt", "")
    if not alt:
        return ["No specific organic alternative data available."]
    return [a.strip() for a in alt.split(",")]


def get_overuse_warnings(nitrogen: float, potassium: float, phosphorous: float) -> list[str]:
    warnings = []
    if nitrogen > 40:
        warnings.append("🔴 Nitrogen overuse detected – risk of groundwater pollution.")
    if potassium > 18:
        warnings.append("🟡 High Potassium – monitor for micronutrient imbalance.")
    if phosphorous > 38:
        warnings.append("🔴 Phosphorous overuse – can cause soil hardening over time.")
    return warnings
