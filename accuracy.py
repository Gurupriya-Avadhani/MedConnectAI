import os
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, r2_score

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_DIR = os.path.join(BASE_DIR, "..", "datasets")
ML_DIR = os.path.join(BASE_DIR, "ml_models")
os.makedirs(ML_DIR, exist_ok=True)

appt_path = os.path.join(DATASET_DIR, "healthcare_appointments.csv")
wait_path = os.path.join(DATASET_DIR, "hospital_wait_times.xlsx")

appointments = pd.read_csv(appt_path) if os.path.exists(appt_path) else pd.DataFrame()

# -------------------------------------
# PREPROCESSING FOR CLASSIFICATION MODEL
# -------------------------------------

if "Gender" in appointments.columns:
    le_gender = LabelEncoder()
    appointments["Gender Encoded"] = le_gender.fit_transform(appointments["Gender"].astype(str))
else:
    appointments["Gender Encoded"] = 0

if "Neighbourhood" in appointments.columns:
    le_neighbourhood = LabelEncoder()
    appointments["Neighbourhood Encoded"] = le_neighbourhood.fit_transform(appointments["Neighbourhood"].astype(str))
else:
    appointments["Neighbourhood Encoded"] = 0

if "Age" not in appointments.columns:
    appointments["Age"] = 30

if len(appointments) == 0:
    X_doctor = [[0, 30, 0]]
    y_doctor = [0]
else:
    X_doctor = appointments[["Gender Encoded", "Age", "Neighbourhood Encoded"]].fillna(0).values
    y_doctor = appointments["No-show"].fillna(0).values if "No-show" in appointments.columns else [0] * len(appointments)

# Split for accuracy
X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(
    X_doctor, y_doctor, test_size=0.2, random_state=42
)

# Train model
doctor_model = RandomForestClassifier(n_estimators=100, random_state=42)
doctor_model.fit(X_train_d, y_train_d)

# Predict + accuracy
y_pred_d = doctor_model.predict(X_test_d)
doctor_accuracy = accuracy_score(y_test_d, y_pred_d)

with open(os.path.join(ML_DIR, "doctor_model.pkl"), "wb") as f:
    pickle.dump(doctor_model, f)

# -------------------------
# PREPROCESSING FOR REGRESSOR
# -------------------------

wait_times = pd.read_excel(wait_path, engine="openpyxl") if os.path.exists(wait_path) else pd.DataFrame()

if "Entry Time" in wait_times.columns and "Completion Time" in wait_times.columns:
    wait_times["Entry Time"] = pd.to_timedelta(wait_times["Entry Time"].astype(str))
    wait_times["Completion Time"] = pd.to_timedelta(wait_times["Completion Time"].astype(str))
    wait_times["wait_minutes"] = (wait_times["Completion Time"] - wait_times["Entry Time"]).dt.total_seconds() / 60
else:
    wait_times["wait_minutes"] = 5

if "Doctor Type" in wait_times.columns:
    le_doctor_type = LabelEncoder()
    wait_times["Doctor Type Encoded"] = le_doctor_type.fit_transform(wait_times["Doctor Type"].astype(str))
else:
    wait_times["Doctor Type Encoded"] = 0

if "Patient Type" in wait_times.columns:
    le_patient_type = LabelEncoder()
    wait_times["Patient Type Encoded"] = le_patient_type.fit_transform(wait_times["Patient Type"].astype(str))
else:
    wait_times["Patient Type Encoded"] = 0

if len(wait_times) == 0:
    X_wait = [[0, 0]]
    y_wait = [5]
else:
    X_wait = wait_times[["Doctor Type Encoded", "Patient Type Encoded"]].fillna(0).values
    y_wait = wait_times["wait_minutes"].fillna(5).values

# Split for R2
X_train_w, X_test_w, y_train_w, y_test_w = train_test_split(
    X_wait, y_wait, test_size=0.2, random_state=42
)

# Train model
wait_time_model = RandomForestRegressor(n_estimators=100, random_state=42)
wait_time_model.fit(X_train_w, y_train_w)

# Predict + R2 score
y_pred_w = wait_time_model.predict(X_test_w)
wait_r2 = r2_score(y_test_w, y_pred_w)

with open(os.path.join(ML_DIR, "wait_time_model.pkl"), "wb") as f:
    pickle.dump(wait_time_model, f)

# -------------------------
# FINAL OUTPUT
# -------------------------
print("=====================================")
print("✅ Models trained and saved successfully!")
print("📁 Saved in:", ML_DIR)
print("📊 Doctor Model Accuracy:", doctor_accuracy)
print("📈 Wait Time Model R² Score:", wait_r2)
print("=====================================")