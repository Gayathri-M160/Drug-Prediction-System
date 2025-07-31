import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
import joblib

# Load your dataset
df = pd.read_csv("drug_data.csv")

# Encode categorical input features
le_sex = LabelEncoder()
le_bp = LabelEncoder()
le_chol = LabelEncoder()

df["Sex"] = le_sex.fit_transform(df["Sex"])
df["BP"] = le_bp.fit_transform(df["BP"])
df["Cholesterol"] = le_chol.fit_transform(df["Cholesterol"])

# Split input and output
X = df[["Sex", "BP", "Cholesterol", "Age", "Na", "K", "Pulse", "Sugar", "BMI"]]
y = df["Drug"]  # Don't encode y if it's already categorical labels

# Train model
model = DecisionTreeClassifier()
model.fit(X, y)



# Save model
joblib.dump(model, "drug_model.pkl")

# Save encoders (for input only)
joblib.dump((le_sex, le_bp, le_chol), "encoders.pkl")

