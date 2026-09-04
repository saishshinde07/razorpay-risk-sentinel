import pandas as pd
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
import joblib

# Load your strictly held-out test set and model
df = pd.read_csv("data/held_out_test.csv") 
model = joblib.load("detector.pkl")

# Assuming 'Class' is the target and the rest are features
X_test = df.drop(columns=["Class"])
y_test = df["Class"]

# Get probabilities
probs = model.predict_proba(X_test)[:, 1]

# Set threshold (Ensure this was decided on a VALIDATION set, not this test set)
threshold = 0.60
y_pred = (probs >= threshold).astype(int)

# Calculate metrics
cm = confusion_matrix(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("### Drop this exactly into your README.md:\n")
print(f"**Precision:** {precision:.1%} | **Recall:** {recall:.1%} | **F1-Score:** {f1:.1%}\n")
print("| | Predicted: Legitimate | Predicted: Fraud (Spike) |")
print("|---|---|---|")
print(f"| **Actual: Legitimate** | {cm[0][0]} (True Negatives) | {cm[0][1]} (False Positives) |")
print(f"| **Actual: Fraud** | {cm[1][0]} (False Negatives) | {cm[1][1]} (True Positives) |")