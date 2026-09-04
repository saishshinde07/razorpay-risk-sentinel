import pandas as pd
import numpy as np
import lightgbm as lgb
import pickle
import os

def process_and_train():
    print("1. Loading Real Kaggle Data...")
    file_path = "../data/creditcard.csv"
    if not os.path.exists(file_path):
        print(f"❌ Error: Could not find {file_path}. Please download it from Kaggle.")
        return
        
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} transactions.")

    print("2. Data Preparation (Chronological Formatting)...")
    # Convert seconds to a mock timestamp for rolling windows
    start_time = pd.to_datetime("2026-09-01 00:00:00")
    df['timestamp'] = start_time + pd.to_timedelta(df['Time'], unit='s')
    df = df.sort_values('timestamp').reset_index(drop=True)

    print("3. Data Splitting (Strict Held-Out Test Set)...")
    # 70% Train, 30% Held-Out Test
    split_idx = int(len(df) * 0.70)
    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()

    # Save the held-out test set so our evaluator and streaming server can use it later
    test_df.to_csv("../data/held_out_test.csv", index=False)
    print(f"Locked away {len(test_df)} transactions into '../data/held_out_test.csv'.")

    print("4. Feature Engineering (180s Rolling Window on Train Data)...")
    train_df = train_df.set_index('timestamp')
    train_df['feat_velocity'] = train_df['Amount'].rolling('180s').count()
    train_df['feat_mean_amount'] = train_df['Amount'].rolling('180s').mean().fillna(0)
    train_df = train_df.reset_index()

    # We use our custom time features + a few inherent Kaggle features for accuracy
    features = ['Amount', 'feat_velocity', 'feat_mean_amount', 'V1', 'V2', 'V3', 'V4', 'V14']
    
    X_train = train_df[features]
    y_train = train_df['Class']

    print("5. Model Building & Training (LightGBM)...")
    # 'balanced' class weight is critical for highly imbalanced fraud data
    model = lgb.LGBMClassifier(
        n_estimators=100, 
        learning_rate=0.05,
        max_depth=5,
        random_state=42, 
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)

    print("6. Model Deployment (Saving Artifacts)...")
    with open("detector.pkl", "wb") as f:
        pickle.dump({"model": model, "features": features}, f)
        
    print("✅ Strict ML Pipeline Complete. Model saved to detector.pkl!")

if __name__ == "__main__":
    process_and_train()