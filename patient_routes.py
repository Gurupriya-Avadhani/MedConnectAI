# patient_routes.py (final)
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from backend.models import Patient, Doctor, Appointment, Notification
from backend.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

patient_bp = Blueprint("patient_bp", __name__)

@patient_bp.route("/register", methods=["GET","POST"])
def patient_register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        contact = request.form.get("contact","")
        age = request.form.get("age")
        gender = request.form.get("gender")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        existing = Patient.query.filter_by(email=email).first()
        if existing:
            return render_template("patient_register.html", error="Patient already registered")
        new_patient = Patient(
            name=name,
            email=email,
            password=generate_password_hash(password),
            contact=contact,
            age=int(age) if age else None,
            gender=gender,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None
        )
        db.session.add(new_patient)
        db.session.commit()
        # create a welcome notification (optional)
        try:
            import requests
            requests.post("http://127.0.0.1:5000/api/llm/refresh_context")
        except Exception:
            pass

        try:
            welcome = Notification(
                patient_id=new_patient.patient_id,
                message=f"Welcome {new_patient.name}! Your account was created successfully.",
                sent_time=datetime.now()
            )
            db.session.add(welcome)
            db.session.commit()
        except Exception:
            db.session.rollback()
        session["patient_id"] = new_patient.patient_id
        session["user_type"] = "patient"
        session["username"] = new_patient.name
        return redirect(url_for("patient_bp.patient_dashboard"))
    return render_template("patient_register.html")

@patient_bp.route("/login", methods=["GET","POST"])
def patient_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        patient = Patient.query.filter_by(email=email).first()
        if patient and check_password_hash(patient.password, password):
            session["patient_id"] = patient.patient_id
            session["user_type"] = "patient"
            session["username"] = patient.name
            return redirect(url_for("patient_bp.patient_dashboard"))
        return render_template("patient_login.html", error="Invalid credentials")
    return render_template("patient_login.html")

@patient_bp.route("/dashboard")
def patient_dashboard():
    patient_id = session.get("patient_id")
    if not patient_id:
        return redirect(url_for("patient_bp.patient_login"))
    patient = Patient.query.get(patient_id)
    doctors = Doctor.query.filter_by(available=True).all()
    appointments = Appointment.query.filter_by(patient_id=patient_id).all()
    return render_template("patient_dashboard.html", patient=patient, doctors=doctors, appointments=appointments)

@patient_bp.route("/book_appointment", methods=["POST"])
def book_appointment():
    data = request.get_json()
    doctor_id = data.get("doctor_id")
    patient_id = session.get("patient_id")
    emergency = data.get("emergency", False)
    if not doctor_id or not patient_id:
        return jsonify({"error":"doctor_id and patient_id required"}),400
    # verify doctor exists
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error":"doctor not found"}),404
    if emergency:
        today = datetime.now().date()
        existing = Appointment.query.filter_by(patient_id=patient_id,status="Emergency",appointment_date=today).first()
        if existing:
            return jsonify({"error":"Emergency slot already used today"}),403
    appointment = Appointment(
        doctor_id=doctor_id,
        patient_id=patient_id,
        appointment_date=datetime.now().date(),
        appointment_time=datetime.now().time().replace(microsecond=0),
        status="Emergency" if emergency else "Booked"
    )
    db.session.add(appointment)
    db.session.commit()
    # Notification for patient (stored in notifications table)
    try:
        notif = Notification(
            patient_id=patient_id,
            message=f"Your appointment with Dr. {doctor.name} has been booked ({'Emergency' if emergency else 'Regular'}).",
            sent_time=datetime.now()
        )
        db.session.add(notif)
        db.session.commit()
    except Exception:
        db.session.rollback()
    return jsonify({"message":"Appointment booked successfully"}),201

@patient_bp.route("/logout")
def patient_logout():
    session.clear()
    return redirect(url_for("patient_bp.patient_login"))

@patient_bp.route("/delete_account", methods=["POST"])
def delete_account():
    patient_id = session.get("patient_id")
    if not patient_id:
        return jsonify({"error":"Not logged in"}),403
    patient = Patient.query.get(patient_id)
    if patient:
        Appointment.query.filter_by(patient_id=patient_id).delete()
        Notification.query.filter_by(patient_id=patient_id).delete()
        db.session.delete(patient)
        db.session.commit()
    session.clear()
    return jsonify({"message":"Account deleted successfully"}),200



# from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
# from backend.models import Patient, Doctor, Appointment, Notification
# from backend.db import db
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import datetime

# patient_bp = Blueprint("patient_bp", __name__)

# @patient_bp.route("/register", methods=["GET","POST"])
# def patient_register():
#     if request.method == "POST":
#         name = request.form.get("name")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         contact = request.form.get("contact","")
#         age = request.form.get("age")
#         gender = request.form.get("gender")
#         latitude = request.form.get("latitude")
#         longitude = request.form.get("longitude")
#         existing = Patient.query.filter_by(email=email).first()
#         if existing:
#             return render_template("patient_register.html", error="Patient already registered")
#         new_patient = Patient(
#             name=name,
#             email=email,
#             password=generate_password_hash(password),
#             contact=contact,
#             age=int(age) if age else None,
#             gender=gender,
#             latitude=float(latitude) if latitude else None,
#             longitude=float(longitude) if longitude else None
#         )
#         db.session.add(new_patient)
#         db.session.commit()
#         try:
#             import requests
#             requests.post("http://127.0.0.1:5000/api/llm/refresh_context")
#         except Exception:
#             pass
#         try:
#             welcome = Notification(
#                 patient_id=new_patient.patient_id,
#                 message=f"Welcome {new_patient.name}! Your account was created successfully.",
#                 sent_time=datetime.now()
#             )
#             db.session.add(welcome)
#             db.session.commit()
#         except Exception:
#             db.session.rollback()
#         session["patient_id"] = new_patient.patient_id
#         return redirect(url_for("patient_bp.patient_dashboard"))
#     return render_template("patient_register.html")


# @patient_bp.route("/login", methods=["GET","POST"])
# def patient_login():
#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("password")
#         patient = Patient.query.filter_by(email=email).first()
#         if not patient or not check_password_hash(patient.password, password):
#             return render_template("login_patient.html", error="Invalid credentials")
#         session["patient_id"] = patient.patient_id
#         return redirect(url_for("patient_bp.patient_dashboard"))
#     return render_template("login_patient.html")


# @patient_bp.route("/dashboard")
# def patient_dashboard():
#     pid = session.get("patient_id")
#     if not pid:
#         return redirect(url_for("patient_bp.patient_login"))
#     patient = Patient.query.get(pid)
#     return render_template("patient_dashboard.html", patient=patient)


# @patient_bp.route("/book_appointment", methods=["POST"])
# def book_appointment():
#     data = request.get_json(silent=True) or {}
#     pid = session.get("patient_id")
#     if not pid:
#         return jsonify({"error":"Not logged in"}), 401
#     doctor_id = data.get("doctor_id")
#     emergency = data.get("emergency", False)
#     doctor = Doctor.query.get(doctor_id)
#     if not doctor:
#         return jsonify({"error":"Doctor not found"}), 404
#     new_appt = Appointment(
#         doctor_id=doctor.doctor_id,
#         patient_id=pid,
#         appointment_date=datetime.now().date(),
#         appointment_time=datetime.now().time(),
#         status="booked",
#         start_time=None,
#         end_time=None,
#         wait_time=None
#     )
#     db.session.add(new_appt)
#     db.session.commit()
#     return jsonify({"message":"Appointment booked","appointment_id": new_appt.appointment_id}), 201


# @patient_bp.route("/delete_account", methods=["POST"])
# def delete_account():
#     pid = session.get("patient_id")
#     if not pid:
#         return jsonify({"error":"Not logged in"}), 401
#     patient = Patient.query.get(pid)
#     if not patient:
#         return jsonify({"error":"Account not found"}), 404
#     try:
#         Appointment.query.filter_by(patient_id=pid).delete()
#         Notification.query.filter_by(patient_id=pid).delete()
#         db.session.delete(patient)
#         db.session.commit()
#     except Exception:
#         db.session.rollback()
#         return jsonify({"error":"Failed to delete account"}), 500
#     session.pop("patient_id", None)
#     return redirect(url_for("index"))


# @patient_bp.route("/logout")
# def logout():
#     session.pop("patient_id", None)
#     return redirect(url_for("index"))
