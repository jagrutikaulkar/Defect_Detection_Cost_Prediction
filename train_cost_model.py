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
    Generate synthetic cost dataset with ENHANCED features
    Includes realistic industry parameters
    """
    
    print("✓ Generating enhanced cost dataset with industry parameters...")
    
    data = []
    
    # Industry parameters (from user input)
    MACHINE_HOUR_RATE = 3000  # ₹/hour
    ENERGY_COST_PER_KWH = 8    # ₹/kWh
    SCRAP_LOSS_PER_DEFECT = 120  # ₹
    PRODUCTION_VOLUME_IMPACT = 5  # %
    
    # Generate 5000 samples (increased for better training)
    for i in range(5000):
        # Features - ENHANCED
        defect_type = random.randint(0, 5)  # 0-5 for 6 defect types
        defect_area = random.uniform(0.5, 100)  # Defect area %
        severity = random.randint(1, 3)  # 1=low, 2=medium, 3=high
        machine_time = random.uniform(0.5, 10)  # Hours
        labor_cost_rate = random.randint(200, 1000)  # Hourly rate
        material_cost = random.randint(100, 2000)  # Material cost
        energy_consumption = random.uniform(10, 500)  # kWh
        production_volume = random.randint(100, 5000)  # units/batch
        
        # Calculate cost breakdown (realistic formula)
        machine_cost = machine_time * MACHINE_HOUR_RATE
        energy_cost = energy_consumption * ENERGY_COST_PER_KWH
        labor_cost = machine_time * labor_cost_rate
        scrap_loss = SCRAP_LOSS_PER_DEFECT * severity * (defect_area / 10)
        production_loss = (production_volume * PRODUCTION_VOLUME_IMPACT / 100) * material_cost / 1000
        
        # Total cost
        total_cost = material_cost + labor_cost + machine_cost + energy_cost + scrap_loss + production_loss
        
        data.append([
            defect_type, defect_area, severity,
            machine_time, labor_cost_rate, material_cost,
            energy_consumption, production_volume, total_cost
        ])
    
    # Create DataFrame with enhanced features
    df = pd.DataFrame(data, columns=[
        'defect_type', 'defect_area', 'severity',
        'machine_time', 'labor_cost_rate', 'material_cost',
        'energy_consumption', 'production_volume', 'cost'
    ])
    
    print(f"✓ Generated {len(df)} cost samples with enhanced features")
    print(f"\nDataset Statistics:")
    print(f"  Cost range: ₹{df['cost'].min():.0f} - ₹{df['cost'].max():.0f}")
    print(f"  Mean cost: ₹{df['cost'].mean():.0f}")
    print(f"  Median cost: ₹{df['cost'].median():.0f}")
    print(f"\nFeature ranges:")
    print(f"  Defect area: {df['defect_area'].min():.1f}% - {df['defect_area'].max():.1f}%")
    print(f"  Machine time: {df['machine_time'].min():.1f}h - {df['machine_time'].max():.1f}h")
    print(f"  Energy consumption: {df['energy_consumption'].min():.0f} - {df['energy_consumption'].max():.0f} kWh")
    
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
    
    # Train model - Enhanced model with better parameters
    print("\n✓ Training Enhanced RandomForest Regressor...")
    print("  Parameters: n_estimators=300, max_depth=20, min_samples_split=5")
    model = RandomForestRegressor(
        n_estimators=300,          # More trees for better accuracy
        max_depth=20,              # Deeper trees for complex relationships
        min_samples_split=5,       # Better generalization
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        verbose=0
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    print("\n" + "=" * 60)
    print("Model Evaluation")
    print("=" * 60)
    
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    
    print(f"Training MAE: ₹{train_mae:.2f}")
    print(f"Test MAE: ₹{test_mae:.2f}")
    print(f"Training R²: {train_r2:.4f}")
    print(f"Test R²: {test_r2:.4f}")
    
    # Feature importance - ENHANCED
    print(f"\n=== Enhanced Feature Importance ===")
    feature_importance = sorted(
        zip(X.columns, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True
    )
    for feat, importance in feature_importance:
        bar_length = int(importance * 50)
        bar = '█' * bar_length
        print(f"  {feat:20s} │{bar} {importance:.4f}")
    
    # Save model
    print(f"\n✓ Saving enhanced model to models/cost_model.pkl...")
    import os
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/cost_model.pkl")
    
    print("\n" + "=" * 60)
    print("✓ ENHANCED COST MODEL TRAINING COMPLETE!")
    print("=" * 60)
    print(f"Model saved to: models/cost_model.pkl")
    print(f"Number of features: {len(X.columns)}")
    print(f"Features: {list(X.columns)}")
    print("=" * 60)


if __name__ == "__main__":
    train_cost_model()
