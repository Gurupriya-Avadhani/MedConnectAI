# backend/routes/notification_routes.py
from flask import Blueprint, jsonify, request
from backend.db import db
from backend.models import Notification
from datetime import datetime

notification_bp = Blueprint("notification_bp", __name__)

@notification_bp.route("/", methods=["POST"])
def add_notification():
    data = request.get_json() or {}
    patient_id = data.get("patient_id")
    message = data.get("message")
    if not message:
        return jsonify({"error": "Message required"}), 400

    note = Notification(patient_id=patient_id, message=message, sent_time=datetime.now())
    db.session.add(note)
    db.session.commit()
    return jsonify({"message": "Notification saved"}), 201

@notification_bp.route("/all", methods=["GET"])
def get_notifications():
    notes = Notification.query.order_by(Notification.sent_time.desc()).limit(50).all()
    return jsonify([
        {
            "notification_id": n.notification_id,
            "patient_id": n.patient_id,
            "message": n.message,
            "sent_time": str(n.sent_time)
        }
        for n in notes
    ])
