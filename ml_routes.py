from flask import Blueprint, request, jsonify
import joblib, os

ml_bp = Blueprint("ml_bp", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_DIR = os.path.join(BASE_DIR, "ml_models")

wait_time_model = None
doctor_model = None

try:
    wait_time_model = joblib.load(os.path.join(MODEL_DIR, "wait_time_model.pkl"))
except Exception:
    wait_time_model = None

try:
    doctor_model = joblib.load(os.path.join(MODEL_DIR, "doctor_model.pkl"))
except Exception:
    doctor_model = None


@ml_bp.route("/predict_wait_time", methods=["POST"])
def predict_wait_time():
    data = request.get_json(silent=True) or {}
    if not wait_time_model:
        return jsonify({"error": "Wait time model not loaded"}), 500
    features = data.get("features")
    try:
        pred = wait_time_model.predict([features])
        return jsonify({"predicted_wait_time_minutes": round(float(pred[0]), 2)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ml_bp.route("/suggest_doctor", methods=["POST"])
def suggest_doctor():
    data = request.get_json(silent=True) or {}
    if not doctor_model:
        return jsonify({"error": "Doctor suggestion model not loaded"}), 500
    features = data.get("features")
    try:
        pred = doctor_model.predict([features])
        return jsonify({"suggested_doctor_id": int(pred[0])})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
