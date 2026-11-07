import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix
from sklearn.model_selection import cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBClassifier
import joblib

class ModelTrainer:
    def __init__(self, models_dir, outputs_dir):
        """
        Initialize the trainer.
        :param models_dir: Directory to save the best model.
        :param outputs_dir: Directory to save plots and reports.
        """
        self.models_dir = models_dir
        self.outputs_dir = outputs_dir
        
        # Ensure directories exist
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.outputs_dir, exist_ok=True)
        
        # Initialize dictionary of models
        self.base_models = {
            'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
            'Decision Tree': DecisionTreeClassifier(random_state=42),
            'Random Forest': RandomForestClassifier(random_state=42),
            'SVM': SVC(probability=True, random_state=42),
            'KNN': KNeighborsClassifier(),
            'Naive Bayes': GaussianNB(),
            'XGBoost': XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)
        }
        self.trained_models = {}
        self.results = {}

    def train_and_evaluate_all(self, X_train, X_test, y_train, y_test):
        """
        Train base models and calculate performance metrics.
        """
        print("[*] Training and evaluating base models...")
        
        for name, model in self.base_models.items():
            print(f"    -> Training {name}...")
            # Fit model
            model.fit(X_train, y_train)
            
            # Predict
            y_pred = model.predict(X_test)
            y_train_pred = model.predict(X_train)
            
            # Calculate metrics
            test_accuracy = accuracy_score(y_test, y_pred)
            train_accuracy = accuracy_score(y_train, y_train_pred)
            
            # Overfitting gap
            overfitting_gap = train_accuracy - test_accuracy
            
            precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted', zero_division=0)
            
            # Cross-validation score (5-Fold CV)
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
            cv_mean = np.mean(cv_scores)
            cv_std = np.std(cv_scores)
            
            self.results[name] = {
                'Train Accuracy': train_accuracy,
                'Test Accuracy': test_accuracy,
                'Overfitting Gap': overfitting_gap,
                'Precision': precision,
                'Recall': recall,
                'F1 Score': f1,
                'CV Mean Accuracy': cv_mean,
                'CV Std Accuracy': cv_std
            }
            
            # Store trained model
            self.trained_models[name] = model
            print(f"       Test Accuracy: {test_accuracy:.4f} | CV Mean Accuracy: {cv_mean:.4f} | Overfitting Gap: {overfitting_gap:.4f}")
            
        return self.results

    def tune_hyperparameters(self, X_train, y_train):
        """
        Optimize Random Forest, XGBoost, and SVM using GridSearchCV.
        """
        print("[*] Tuning hyperparameters for selected models...")
        
        # 1. Random Forest tuning
        print("    -> Tuning Random Forest...")
        rf_param_grid = {
            'n_estimators': [50, 100, 150],
            'max_depth': [None, 8, 12],
            'min_samples_split': [2, 5]
        }
        rf_grid = GridSearchCV(RandomForestClassifier(random_state=42), rf_param_grid, cv=3, scoring='accuracy', n_jobs=-1)
        rf_grid.fit(X_train, y_train)
        print(f"       Best RF Parameters: {rf_grid.best_params_} (Accuracy: {rf_grid.best_score_:.4f})")
        self.trained_models['Random Forest (Tuned)'] = rf_grid.best_estimator_
        
        # 2. XGBoost tuning
        print("    -> Tuning XGBoost...")
        xgb_param_grid = {
            'n_estimators': [50, 100],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.05, 0.1, 0.2]
        }
        xgb_grid = GridSearchCV(XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42), 
                               xgb_param_grid, cv=3, scoring='accuracy', n_jobs=-1)
        xgb_grid.fit(X_train, y_train)
        print(f"       Best XGBoost Parameters: {xgb_grid.best_params_} (Accuracy: {xgb_grid.best_score_:.4f})")
        self.trained_models['XGBoost (Tuned)'] = xgb_grid.best_estimator_
        
        # 3. SVM tuning
        print("    -> Tuning SVM...")
        svm_param_grid = {
            'C': [0.1, 1, 10],
            'kernel': ['linear', 'rbf'],
            'gamma': ['scale', 'auto']
        }
        svm_grid = GridSearchCV(SVC(probability=True, random_state=42), svm_param_grid, cv=3, scoring='accuracy', n_jobs=-1)
        svm_grid.fit(X_train, y_train)
        print(f"       Best SVM Parameters: {svm_grid.best_params_} (Accuracy: {svm_grid.best_score_:.4f})")
        self.trained_models['SVM (Tuned)'] = svm_grid.best_estimator_
        
        # Evaluate tuned models
        for name in ['Random Forest (Tuned)', 'XGBoost (Tuned)', 'SVM (Tuned)']:
            model = self.trained_models[name]
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
            cv_mean = np.mean(cv_scores)
            
            # Full metrics
            y_train_pred = model.predict(X_train)
            # Find matching test set targets outside in evaluate_tuned_on_test
            
    def evaluate_tuned_on_test(self, X_train, X_test, y_train, y_test):
        """
        Evaluate the newly tuned models on the test set.
        """
        print("[*] Evaluating tuned models on test set...")
        tuned_names = ['Random Forest (Tuned)', 'XGBoost (Tuned)', 'SVM (Tuned)']
        
        for name in tuned_names:
            if name not in self.trained_models:
                continue
            model = self.trained_models[name]
            y_pred = model.predict(X_test)
            y_train_pred = model.predict(X_train)
            
            test_accuracy = accuracy_score(y_test, y_pred)
            train_accuracy = accuracy_score(y_train, y_train_pred)
            overfitting_gap = train_accuracy - test_accuracy
            precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted', zero_division=0)
            
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
            cv_mean = np.mean(cv_scores)
            cv_std = np.std(cv_scores)
            
            self.results[name] = {
                'Train Accuracy': train_accuracy,
                'Test Accuracy': test_accuracy,
                'Overfitting Gap': overfitting_gap,
                'Precision': precision,
                'Recall': recall,
                'F1 Score': f1,
                'CV Mean Accuracy': cv_mean,
                'CV Std Accuracy': cv_std
            }
            print(f"       {name} Test Accuracy: {test_accuracy:.4f} | CV Mean: {cv_mean:.4f} | Overfitting Gap: {overfitting_gap:.4f}")

    def select_and_save_best_model(self, X_train, X_test, y_train, y_test, label_encoder):
        """
        Automatically compare all models and select the best model based on:
        - Highest test accuracy
        - Low overfitting (overfitting gap <= 0.05 if possible, or lowest overall gap for high-performing models)
        - Save selected best model to 'best_crop_model.pkl'.
        """
        print("[*] Starting Automatic Best Model Selection...")
        results_df = pd.DataFrame(self.results).T
        results_df.to_csv(os.path.join(self.outputs_dir, 'model_comparison.csv'), index_label='Model')
        print(f"[+] Model comparison saved to {os.path.join(self.outputs_dir, 'model_comparison.csv')}")
        
        # Selection logic:
        # 1. Filter out models with excessive overfitting (overfitting gap > 0.08) if there are models with <= 0.08 and Test Accuracy >= 0.90
        # 2. Select model with the highest CV Mean Accuracy (which represents generalization best), else Test Accuracy
        candidates = results_df.copy()
        
        # Filter where Overfitting Gap is reasonable (less than 5-8% difference)
        reasonable_overfit = candidates[candidates['Overfitting Gap'] <= 0.08]
        if not reasonable_overfit.empty:
            best_model_name = reasonable_overfit['Test Accuracy'].idxmax()
        else:
            best_model_name = candidates['Test Accuracy'].idxmax()
            
        best_metrics = self.results[best_model_name]
        print(f"\n==================================================")
        print(f"   [BEST MODEL SELECTED] {best_model_name}")
        print(f"   - Train Accuracy: {best_metrics['Train Accuracy']:.4f}")
        print(f"   - Test Accuracy:  {best_metrics['Test Accuracy']:.4f}")
        print(f"   - CV Mean Accuracy: {best_metrics['CV Mean Accuracy']:.4f}")
        print(f"   - F1 Score:       {best_metrics['F1 Score']:.4f}")
        print(f"   - Overfitting Gap: {best_metrics['Overfitting Gap']:.4f}")
        print(f"==================================================")
        
        # Save best model
        best_model = self.trained_models[best_model_name]
        best_model_path = os.path.join(self.models_dir, 'best_crop_model.pkl')
        joblib.dump(best_model, best_model_path)
        print(f"[+] Best model saved successfully to {best_model_path}")
        
        # Generate classification outputs
        y_pred = best_model.predict(X_test)
        
        # 1. Save Confusion Matrix
        plt.figure(figsize=(12, 10))
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', 
                    xticklabels=label_encoder.classes_, 
                    yticklabels=label_encoder.classes_)
        plt.title(f'Confusion Matrix - {best_model_name}', fontsize=16, fontweight='bold', pad=15)
        plt.xlabel('Predicted Label', fontsize=12, labelpad=10)
        plt.ylabel('True Label', fontsize=12, labelpad=10)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        cm_path = os.path.join(self.outputs_dir, 'best_model_confusion_matrix.png')
        plt.savefig(cm_path, dpi=300)
        plt.close()
        print(f"[+] Confusion Matrix plot saved to {cm_path}")
        
        # 2. Save Classification Report
        report_str = classification_report(y_test, y_pred, target_names=label_encoder.classes_)
        report_path = os.path.join(self.outputs_dir, 'best_model_classification_report.txt')
        with open(report_path, 'w') as f:
            f.write(f"Best Model: {best_model_name}\n")
            f.write("="*50 + "\n\n")
            f.write(report_str)
        print(f"[+] Classification Report saved to {report_path}")
        
        # 3. Save Model Comparison Accuracy Chart
        plt.figure(figsize=(10, 6))
        sns.set_theme(style="whitegrid")
        comparison_sorted = results_df.sort_values(by='Test Accuracy', ascending=False).reset_index()
        ax = sns.barplot(x='index', y='Test Accuracy', data=comparison_sorted, palette='viridis')
        plt.title('Model Accuracy Comparison', fontsize=14, fontweight='bold', pad=12)
        plt.xlabel('Model Name', fontsize=11, labelpad=8)
        plt.ylabel('Test Accuracy', fontsize=11, labelpad=8)
        plt.ylim(0.8, 1.02)
        plt.xticks(rotation=30, ha='right')
        
        # Add labels on top of bars
        for p in ax.patches:
            height = p.get_height()
            ax.text(p.get_x() + p.get_width()/2., height + 0.005, f'{height:.4f}', ha="center", fontsize=9, fontweight='semibold')
            
        plt.tight_layout()
        comparison_chart_path = os.path.join(self.outputs_dir, 'model_accuracy_comparison.png')
        plt.savefig(comparison_chart_path, dpi=300)
        plt.close()
        print(f"[+] Model Accuracy Comparison chart saved to {comparison_chart_path}")
        
        return best_model_name, best_metrics
