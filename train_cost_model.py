"""
Train Cost Prediction Model (Regression)
Simple Random Forest implementation

Run: python train_cost_model.py
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import random

def generate_cost_dataset():
    """
    Generate synthetic cost dataset
    Since NEU-DET doesn't have cost labels, we create realistic synthetic data
    """
    
    print("✓ Generating synthetic cost dataset...")
    
    data = []
    
    # Generate 3000 samples
    for i in range(3000):
        # Features
        defect_type = random.randint(0, 5)  # 0-5 for 6 defect types
        defect_area = random.uniform(5, 40)  # Defect area %
        severity = random.randint(1, 3)  # 1=low, 2=medium, 3=high
        machine_time = random.uniform(1, 4)  # Hours
        labor_cost = random.randint(200, 500)  # Hourly rate
        material_cost = random.randint(100, 400)  # Material cost
        
        # Cost calculation (realistic formula)
        base_cost = material_cost + labor_cost + machine_time * 60
        defect_penalty = defect_area * 5 + severity * 120
        total_cost = base_cost + defect_penalty
        
        data.append([
            defect_type, defect_area, severity,
            machine_time, labor_cost, material_cost, total_cost
        ])
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=[
        'defect_type', 'defect_area', 'severity',
        'machine_time', 'labor_cost', 'material_cost', 'cost'
    ])
    
    print(f"✓ Generated {len(df)} cost samples")
    print(f"\nDataset Statistics:")
    print(f"  Cost range: ₹{df['cost'].min():.0f} - ₹{df['cost'].max():.0f}")
    print(f"  Mean cost: ₹{df['cost'].mean():.0f}")
    
    return df

def train_cost_model():
    """Train cost prediction model"""
    
    print("=" * 60)
    print("Training Cost Prediction Model")
    print("=" * 60)
    
    # Generate dataset
    df = generate_cost_dataset()
    
    # Split features and target
    X = df.drop('cost', axis=1)
    y = df['cost']
    
    print(f"\n✓ Features: {list(X.columns)}")
    print(f"✓ Target: cost")
    
    # Train-test split
    print("\n✓ Splitting to 80% train, 20% test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    print("\n✓ Training RandomForest (n_estimators=200)...")
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    print("\n" + "=" * 60)
    print("Model Evaluation")
    print("=" * 60)
    
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    train_mae = mean_naive_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    
    print(f"Training MAE: ₹{train_mae:.2f}")
    print(f"Test MAE: ₹{test_mae:.2f}")
    print(f"Training R²: {train_r2:.4f}")
    print(f"Test R²: {test_r2:.4f}")
    
    # Feature importance
    print(f"\nFeature Importance:")
    for i, feat in enumerate(X.columns):
        print(f"  {feat}: {model.feature_importances_[i]:.4f}")
    
    # Save model
    print(f"\n✓ Saving model to models/cost_model.pkl...")
    import os
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/cost_model.pkl")
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print(f"Model saved to: models/cost_model.pkl")
    print("=" * 60)

def mean_naive_error(y_true, y_pred):
    """Calculate mean absolute error"""
    return np.mean(np.abs(y_true - y_pred))

if __name__ == "__main__":
    train_cost_model()
