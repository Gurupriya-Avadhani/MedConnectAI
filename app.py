import os
from datetime import datetime
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask_cors import CORS
from flask_socketio import SocketIO
from backend.db import db
from backend.models import Doctor, Patient, Appointment, Notification, Hospital
from backend.routes.llm_routes import llm_bp
from backend.routes.doctor_routes import doctor_bp
from backend.routes.patient_routes import patient_bp
from backend.routes.notification_routes import notification_bp
from backend.routes.ml_routes import ml_bp


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    CORS(app)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, "../database/medconnectai.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Register blueprints
    app.register_blueprint(llm_bp, url_prefix="/api/llm")
    app.register_blueprint(doctor_bp, url_prefix="/doctor")
    app.register_blueprint(patient_bp, url_prefix="/patient")
    app.register_blueprint(notification_bp, url_prefix="/api/notifications")
    app.register_blueprint(ml_bp, url_prefix="/api/ml")

    with app.app_context():
        db.create_all()

    # ---------- ROUTES ----------
    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/choose", methods=["GET", "POST"])
    def choose():
        if request.method == "POST":
            role = request.form.get("role")
            if role == "doctor":
                return redirect(url_for("doctor_bp.doctor_login"))
            return redirect(url_for("patient_bp.patient_login"))
        return render_template("index.html")

    @app.route("/chatbot")
    def chatbot():
        """Direct route to open MedBot chat UI"""
        return render_template("components/chatbot.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("home"))

    @app.route("/delete_account", methods=["POST"])
    def delete_account():
        user_type = session.get("user_type")
        if user_type == "doctor":
            doctor_id = session.get("doctor_id")
            if doctor_id:
                doc = Doctor.query.get(doctor_id)
                if doc:
                    Appointment.query.filter_by(doctor_id=doctor_id).delete()
                    Notification.query.filter_by(patient_id=doctor_id).delete()
                    db.session.delete(doc)
                    db.session.commit()
        elif user_type == "patient":
            patient_id = session.get("patient_id")
            if patient_id:
                pat = Patient.query.get(patient_id)
                if pat:
                    Appointment.query.filter_by(patient_id=patient_id).delete()
                    Notification.query.filter_by(patient_id=patient_id).delete()
                    db.session.delete(pat)
                    db.session.commit()
        session.clear()
        return jsonify({"message": "Account deleted"}), 200

    # API ROUTES
    @app.route("/api/doctors", methods=["GET"])
    def get_doctors():
        doctors = Doctor.query.all()
        return jsonify([{
            "doctor_id": d.doctor_id,
            "name": d.name,
            "specialization": d.specialization,
            "experience": d.experience,
            "contact": d.contact,
            "available": bool(d.available),
            "latitude": d.latitude,
            "longitude": d.longitude,
            "hospital_id": d.hospital_id,
            "hospital_name": d.hospital.name if d.hospital else "Unknown"
        } for d in doctors])

    @app.route("/api/patients", methods=["GET"])
    def get_patients():
        patients = Patient.query.all()
        return jsonify([{
            "patient_id": p.patient_id,
            "name": p.name,
            "age": p.age,
            "gender": p.gender,
            "contact": p.contact
        } for p in patients])

    @app.route("/api/appointments", methods=["GET", "POST"])
    def appointments():
        if request.method == "GET":
            appointments = Appointment.query.all()
            return jsonify([{
                "appointment_id": a.appointment_id,
                "doctor_id": a.doctor_id,
                "patient_id": a.patient_id,
                "appointment_date": str(a.appointment_date),
                "appointment_time": str(a.appointment_time),
                "status": a.status
            } for a in appointments])

        data = request.get_json()
        doctor_id = data.get("doctor_id")
        patient_id = data.get("patient_id")
        emergency = data.get("emergency", False)
        appointment_date = datetime.now().date()
        appointment_time = datetime.now().time().replace(microsecond=0)

        if emergency:
            existing = Appointment.query.filter_by(
                patient_id=patient_id,
                status="Emergency",
                appointment_date=appointment_date
            ).first()
            if existing:
                return jsonify({"error": "Emergency slot already used today"}), 403

        appointment = Appointment(
            doctor_id=doctor_id,
            patient_id=patient_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status="Emergency" if emergency else "Booked"
        )
        db.session.add(appointment)
        db.session.commit()

        try:
            socketio.emit("appointment_update", {
                "appointment_id": appointment.appointment_id,
                "doctor_id": appointment.doctor_id,
                "patient_id": appointment.patient_id,
                "appointment_date": str(appointment.appointment_date),
                "appointment_time": str(appointment.appointment_time),
                "status": appointment.status
            }, broadcast=True)
        except Exception:
            pass

        return jsonify({"message": "Appointment booked successfully"}), 201

    @app.route("/api/doctor/update_availability", methods=["POST"])
    def update_availability():
        data = request.get_json()
        doctor_id = data.get("doctor_id")
        available = data.get("available")
        if doctor_id is None or available is None:
            return jsonify({"error": "doctor_id and available required"}), 400

        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({"error": "Doctor not found"}), 404

        doctor.available = bool(available)
        db.session.commit()

        try:
            socketio.emit("availability_update", {
                "doctor_id": doctor.doctor_id,
                "available": doctor.available
            }, broadcast=True)
        except Exception:
            pass

        return jsonify({"message": "Availability updated"}), 200

    @app.route("/api/notifications/all", methods=["GET"])
    def all_notifications():
        notes = Notification.query.order_by(Notification.sent_time.desc()).limit(50).all()
        return jsonify([{
            "notification_id": n.notification_id,
            "patient_id": n.patient_id,
            "message": n.message,
            "sent_time": str(n.sent_time)
        } for n in notes])

    return app


app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=20)

if __name__ == "__main__":
    print("✅ Database initialized successfully.")
    print("🚀 MedConnectAI Backend is running at: http://127.0.0.1:5000")
    socketio.run(app, debug=True, host="127.0.0.1", port=5000)
