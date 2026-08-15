import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score
import joblib
import os

print("Loading data...")
df = pd.read_csv("ml/data/train_transaction.csv")

print(f"Dataset shape: {df.shape}")
print(f"Fraud rate: {df['isFraud'].mean() * 100:.2f}%")
print(f"Total transactions: {len(df)}")
print(f"Fraud transactions: {df['isFraud'].sum()}")

print("\n--- First 5 columns ---")
print(df.columns[:10].tolist())

print("\n--- Key columns ---")
print(df[['TransactionID', 'TransactionAmt', 'ProductCD', 'isFraud']].head())

print("\n--- Fraud vs Normal amounts ---")
print("Average fraud amount: $", df[df['isFraud']==1]['TransactionAmt'].mean().round(2))
print("Average normal amount: $", df[df['isFraud']==0]['TransactionAmt'].mean().round(2))

print("\nPreparing features...")

# Select only numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# Remove target column
numeric_cols = [col for col in numeric_cols if col != 'isFraud']

# Fill missing values with median
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

# Use subset of data for faster training
X = df[numeric_cols].head(50000)
y = df['isFraud'].head(50000)

print(f"Training with {len(X)} transactions and {len(numeric_cols)} features")

print("\nTraining Isolation Forest model...")
model = IsolationForest(
    contamination=0.035,
    random_state=42,
    n_estimators=100
)

model.fit(X)

print("Model trained!")

# Predict
predictions = model.predict(X)
predictions = [1 if p == -1 else 0 for p in predictions]

print("\n--- Results ---")
print(classification_report(y, predictions))
print(f"AUC-ROC Score: {roc_auc_score(y, predictions):.4f}")

# Save model
joblib.dump(model, 'ml/models/isolation_forest.pkl')
joblib.dump(numeric_cols, 'ml/models/feature_columns.pkl')
print("\nModel saved to ml/models/")