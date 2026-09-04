import pandas as pd
import numpy as np
import pickle
from sklearn.metrics import classification_report, confusion_matrix

def evaluate_real_data():
    print("1. Loading trained Kaggle model...")
    with open("detector.pkl", "rb") as f:
        bundle = pickle.load(f)
        model = bundle["model"]
        features = bundle["features"]

    print("2. Loading strict held-out test set...")
    test_df = pd.read_csv("../data/held_out_test.csv")
    
    print("3. Engineering features on test set...")
    test_df['timestamp'] = pd.to_datetime(test_df['timestamp'])
    test_df = test_df.set_index('timestamp')
    # Recreate the 3-minute rolling windows for the evaluation data
    test_df['feat_velocity'] = test_df['Amount'].rolling('180s').count()
    test_df['feat_mean_amount'] = test_df['Amount'].rolling('180s').mean().fillna(0)
    test_df = test_df.reset_index()

    X_test = test_df[features]
    y_test = test_df['Class']

    print("4. Running evaluation...")
    preds_proba = model.predict_proba(X_test)[:, 1]
    
    # Defense-oriented threshold
    threshold = 0.60
    preds = (preds_proba >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_test, preds).ravel()

    # The Kaggle dataset amounts don't specify currency, but for the Razorpay hackathon,
    # we'll assume a rough INR multiplier to make the business metrics look realistic for India.
    inr_multiplier = 83.0 
    
    legit_holds_val = test_df[(y_test == 0) & (preds == 1)]['Amount'].sum() * inr_multiplier
    fp_rupee_cost = legit_holds_val * 0.015 # 1.5% friction cost
    fraud_loss_val = test_df[(y_test == 1) & (preds == 0)]['Amount'].sum() * inr_multiplier

    print("\n================ FINAL HELD-OUT METRICS ================")
    print(f"Total Transactions Evaluated: {len(test_df)}")
    print(f"True Positives (Spikes Caught):  {tp}")
    print(f"False Positives (False Alarms):  {fp}")
    print(f"False Negatives (Missed Fraud):  {fn}")
    print(f"True Negatives (Correct Clears): {tn}")
    print("\n---------------- MODEL ACCURACY -------------------------")
    print(classification_report(y_test, preds, target_names=["Legitimate", "Fraud Spike"]))
    print("---------------- BUSINESS COST IMPACT -------------------")
    print(f"Legitimate Volume Held:   ₹{legit_holds_val:,.2f}")
    print(f"Calculated FP Cost:       ₹{fp_rupee_cost:,.2f} (merchant friction @ 1.5%)")
    print(f"Unmitigated Fraud Loss:   ₹{fraud_loss_val:,.2f}")
    print("=========================================================\n")

if __name__ == "__main__":
    evaluate_real_data()