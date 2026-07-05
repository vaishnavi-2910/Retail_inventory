import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import pickle
import os

# -----------------------------
# 1. CREATE DATASET
# -----------------------------
data = {
    "crime_rate":       [0.9, 0.2, 0.7, 0.3, 0.8, 0.1, 0.6, 0.4, 0.95, 0.25, 0.85, 0.15],
    "time_risk":        [0.8, 0.1, 0.6, 0.2, 0.9, 0.2, 0.7, 0.3, 0.85, 0.15, 0.8, 0.2],
    "traffic_density":  [0.3, 0.7, 0.4, 0.8, 0.2, 0.9, 0.5, 0.6, 0.3, 0.8, 0.4, 0.7],
    "lighting":         [0.2, 0.9, 0.3, 0.8, 0.1, 0.95, 0.4, 0.7, 0.2, 0.85, 0.3, 0.9],
    "police_presence":  [0.2, 0.8, 0.3, 0.7, 0.1, 0.9, 0.4, 0.6, 0.15, 0.75, 0.35, 0.8],
}

df = pd.DataFrame(data)

# -----------------------------
# 2. TARGET (RISK SCORE)
# -----------------------------
df["risk_score"] = (
    0.4 * df["crime_rate"] +
    0.2 * df["time_risk"] +
    0.15 * (1 - df["traffic_density"]) +
    0.15 * (1 - df["lighting"]) +
    0.1 * (1 - df["police_presence"])
)
X = df.drop("risk_score", axis=1)
y = df["risk_score"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)
preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)

print("\n✅ Model Training Completed")
print("📉 Mean Absolute Error:", mae)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "risk_model.pkl")

with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

print("💾 Model saved at:", MODEL_PATH)

# -----------------------------
# 7. TEST PREDICTION
# -----------------------------
def predict_risk(sample):
    sample = np.array(sample).reshape(1, -1)
    risk = model.predict(sample)[0]
    safety = (1 - risk) * 100
    return risk, safety

if __name__ == "__main__":
    test = [0.8, 0.7, 0.3, 0.2, 0.2]
    risk, safety = predict_risk(test)

    print("\n🧪 Sample Prediction")
    print("Risk:", risk)
    print("Safety Score:", safety)