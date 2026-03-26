from flask import Blueprint, jsonify, request, current_app
from backend.utils.llm_integration import generate_response, _get_live_db_snapshot

llm_bp = Blueprint("llm_bp", __name__)

@llm_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_msg = data.get("message", "")
    with current_app.app_context():
        reply = generate_response(user_msg, request_data=data)
    return jsonify({"reply": reply})

@llm_bp.route("/refresh_context", methods=["POST"])
def refresh_context():
    with current_app.app_context():
        snapshot = _get_live_db_snapshot()
    return jsonify({"message": "Chatbot context refreshed", "snapshot": snapshot}), 200
