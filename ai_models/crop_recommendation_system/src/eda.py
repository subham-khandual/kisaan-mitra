import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier

class EDAVisualizer:
    def __init__(self, outputs_dir):
        """
        Initialize the EDA visualizer.
        :param outputs_dir: Directory to save generated plots.
        """
        self.outputs_dir = outputs_dir
        os.makedirs(self.outputs_dir, exist_ok=True)
        
        # Set visualization theme for premium styling
        sns.set_theme(style="whitegrid")
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

    def generate_all_plots(self, df):
        """
        Run all EDA plot generations.
        :param df: Cleaned DataFrame with standard columns.
        """
        print("[*] Starting Exploratory Data Analysis (EDA) plotting...")
        
        self.plot_correlation_heatmap(df)
        self.plot_crop_distribution(df)
        self.plot_pairplot(df)
        self.plot_feature_importance(df)
        self.plot_soil_and_rainfall_analysis(df)
        
        print("[+] All EDA plots generated and saved successfully!")

    def plot_correlation_heatmap(self, df):
        """
        Generate correlation heatmap of numerical features.
        """
        print("    -> Plotting correlation heatmap...")
        numeric_df = df.drop(columns=['label'])
        corr_matrix = numeric_df.corr()
        
        plt.figure(figsize=(8, 6))
        # Premium color palette: diverging coolwarm or icefire
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, annot=True, mask=mask, cmap='Spectral', fmt='.2f', 
                    linewidths=0.5, annot_kws={"size": 10, "weight": "bold"})
        plt.title('Soil Nutrients & Climate Correlation Heatmap', fontsize=14, fontweight='bold', pad=15)
        plt.tight_layout()
        
        path = os.path.join(self.outputs_dir, 'correlation_heatmap.png')
        plt.savefig(path, dpi=300)
        plt.close()
        print(f"       Saved: {path}")

    def plot_crop_distribution(self, df):
        """
        Generate count chart of crop distribution.
        """
        print("    -> Plotting crop distribution chart...")
        plt.figure(figsize=(12, 6))
        
        # Group and count
        crop_counts = df['label'].value_counts().reset_index()
        crop_counts.columns = ['Crop', 'Count']
        
        ax = sns.barplot(x='Crop', y='Count', data=crop_counts, palette='viridis')
        plt.title('Crop Distribution in Dataset (Sample Count)', fontsize=14, fontweight='bold', pad=12)
        plt.xlabel('Crop Type', fontsize=11, labelpad=8)
        plt.ylabel('Number of Samples', fontsize=11, labelpad=8)
        plt.xticks(rotation=45, ha='right')
        
        # Add sample count text above bars
        for p in ax.patches:
            height = p.get_height()
            ax.text(p.get_x() + p.get_width()/2., height + 1, f'{int(height)}', ha="center", fontsize=8, fontweight='semibold')
            
        plt.tight_layout()
        path = os.path.join(self.outputs_dir, 'crop_distribution.png')
        plt.savefig(path, dpi=300)
        plt.close()
        print(f"       Saved: {path}")

    def plot_pairplot(self, df):
        """
        Generate pairplot of key soil features (N, P, K, pH) colored by crop label.
        Downsampled to keep it extremely fast and lightweight.
        """
        print("    -> Plotting pairplots of key features...")
        # Select representative crops to keep the plot highly readable and beautiful
        unique_crops = df['label'].unique()
        selected_crops = unique_crops[:5]  # Take first 5 crops for premium visualization clarity
        
        df_subset = df[df['label'].isin(selected_crops)].copy()
        
        # Downsample if too large
        if len(df_subset) > 400:
            df_subset = df_subset.sample(n=400, random_state=42)
            
        # Select essential features N, P, K, ph
        plot_features = ['N', 'P', 'K', 'ph', 'label']
        
        g = sns.pairplot(df_subset[plot_features], hue='label', palette='husl', 
                         corner=True, diag_kind='kde', plot_kws={'alpha': 0.7, 's': 30})
        g.fig.suptitle('Pairwise Feature Relationships (Top 5 Crops)', fontsize=14, fontweight='bold', y=1.02)
        
        path = os.path.join(self.outputs_dir, 'feature_pairplots.png')
        g.savefig(path, dpi=300)
        plt.close()
        print(f"       Saved: {path}")

    def plot_feature_importance(self, df):
        """
        Calculate and generate feature importance using Random Forest.
        """
        print("    -> Plotting feature importance graph...")
        X = df.drop(columns=['label'])
        y = df['label']
        
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X, y)
        
        importances = rf.feature_importances_
        feature_names = X.columns
        
        feat_imp = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
        feat_imp = feat_imp.sort_values(by='Importance', ascending=False).reset_index(drop=True)
        
        plt.figure(figsize=(8, 5))
        ax = sns.barplot(x='Importance', y='Feature', data=feat_imp, palette='crest_r')
        plt.title('Crop Decision Feature Importance (Random Forest)', fontsize=14, fontweight='bold', pad=12)
        plt.xlabel('Importance Score', fontsize=11, labelpad=8)
        plt.ylabel('Feature', fontsize=11, labelpad=8)
        
        # Add labels to the bar charts
        for p in ax.patches:
            width = p.get_width()
            ax.text(width + 0.005, p.get_y() + p.get_height()/2., f'{width*100:.2f}%', 
                    va="center", ha="left", fontsize=9, fontweight='semibold')
            
        plt.xlim(0, max(importances) + 0.05)
        plt.tight_layout()
        
        path = os.path.join(self.outputs_dir, 'feature_importance.png')
        plt.savefig(path, dpi=300)
        plt.close()
        print(f"       Saved: {path}")

    def plot_soil_and_rainfall_analysis(self, df):
        """
        Generate rainfall and soil nutrient distribution box plots.
        """
        print("    -> Plotting rainfall and soil analysis charts...")
        
        # 1. Soil Nutrients N, P, K Mean Levels per Crop (Barplot)
        plt.figure(figsize=(14, 6))
        mean_nutrients = df.groupby('label')[['N', 'P', 'K']].mean().reset_index()
        mean_nutrients_melted = pd.melt(mean_nutrients, id_vars=['label'], value_vars=['N', 'P', 'K'],
                                        var_name='Nutrient', value_name='Average Level (mg/kg)')
        
        sns.barplot(x='label', y='Average Level (mg/kg)', hue='Nutrient', data=mean_nutrients_melted, palette='muted')
        plt.title('Average Soil Nutrient (N, P, K) Requirements per Crop', fontsize=14, fontweight='bold', pad=12)
        plt.xlabel('Crop Type', fontsize=11, labelpad=8)
        plt.ylabel('Average Nutrient Level (mg/kg)', fontsize=11, labelpad=8)
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Nutrients')
        plt.tight_layout()
        
        path1 = os.path.join(self.outputs_dir, 'soil_nutrients_analysis.png')
        plt.savefig(path1, dpi=300)
        plt.close()
        print(f"       Saved: {path1}")
        
        # 2. Rainfall Distribution per Crop (Boxplot)
        plt.figure(figsize=(14, 6))
        sns.boxplot(x='label', y='rainfall', data=df, palette='GnBu')
        plt.title('Rainfall Requirement Distribution per Crop', fontsize=14, fontweight='bold', pad=12)
        plt.xlabel('Crop Type', fontsize=11, labelpad=8)
        plt.ylabel('Rainfall (mm)', fontsize=11, labelpad=8)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        path2 = os.path.join(self.outputs_dir, 'rainfall_requirement_analysis.png')
        plt.savefig(path2, dpi=300)
        plt.close()
        print(f"       Saved: {path2}")
